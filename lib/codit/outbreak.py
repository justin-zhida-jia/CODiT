import pandas as pd
import logging
import numpy as np
import math
import matplotlib.pyplot as plt
# according to Leeds accommodations' coordinates distribution's 'lon':'lat' ratio, the unit is inch, real size would fit the distribution
plt.rcParams["figure.figsize"] = [12, 5]
# Need "pip install celluloid", celluloid -- a 3rd-party python lib using matplotlib.animation.ArtistAnimation
from celluloid import Camera

from codit.population.covid import PersonCovid
from codit.population.population import FixedNetworkPopulation

from codit.disease import covid_hazard

def setup_range_for_histogram(pop):
    """
    Establish range of all population coordinates for every heatmap generated later
    :param pop:
    :return: range of all population coordinates on city map e.g. [-1.7776973000000003, -1.3100551999999999, 53.7060248, 53.942890000000006]
    """
    all_pop_coords = [[p.home.coordinate['lon'], p.home.coordinate['lat']] for p in pop.people]
    all_pop_coords_list = list(zip(*all_pop_coords))
    heatmap, xedges, yedges = np.histogram2d(all_pop_coords_list[0], all_pop_coords_list[1], bins=300)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    return extent


class Outbreak:
    def __init__(self, society, disease, pop_size=0, seed_size=0, n_days=0,
                 population=None,
                 population_type=None,
                 person_type=None):

        self.pop = self.prepare_population(pop_size, population, population_type, society, person_type)
        society.clear_queues()
        self.pop.seed_infections(seed_size, disease)

        self.initialize_timers(n_days, society.episodes_per_day)
        self.group_size = society.encounter_size

        self.society = society
        self.disease = disease

        self.set_recorder()

    def prepare_population(self, pop_size, population, population_type, society, person_type):
        if population:
            assert pop_size in (0, len(population.people)), "provide a population of the correct size"
            logging.warning("Using a pre-existing population - does it have the right network structure?")
            if person_type is not None:
                assert {person_type} == set(type(p) for p in population.people), \
                    "The people in this population are of the wrong type"
            population.reset_people(society)
            self.pop = population
            return population

        population_type = population_type or FixedNetworkPopulation
        person_type = person_type or PersonCovid
        return population_type(pop_size, society, person_type=person_type)

    def set_recorder(self, recorder=None):
        self.recorder = recorder or OutbreakRecorder()

    def initialize_timers(self, n_days, enc_per_day):
        self.n_days = n_days
        self.n_periods = n_days * enc_per_day
        self.time_increment = 1 / enc_per_day

        self.time = 0
        self.step_num = 0

    def simulate(self):
        for t in range(self.n_periods):
            self.update_time()
            self.society.manage_outbreak(self.pop)
            self.pop.attack_in_groupings(self.group_size)
            self.record_state()
        # close plt after cameras have been saved to avoid showing single heatmap
        plt.close()
        self.recorder.realized_r0 = self.pop.realized_r0()
        self.recorder.society_config = self.society.cfg
        self.recorder.disease_config = self.disease.cfg
        return self.recorder

    def update_time(self):
        self.pop.update_time()
        self.time += self.time_increment
        self.step_num += 1

    def record_state(self):
        self.recorder.record_step(self)

    def plot(self, **kwargs):
        self.recorder.plot(**kwargs)


class OutbreakRecorder:
    def __init__(self):
        self.story = []
        self.realized_r0 = None
        # initialise fig, camera, and heatmap_range for video generation
        self.fig = plt.figure(dpi=200)
        self.camera = Camera(self.fig)
        self.heatmap_range = []

    def record_step(self, o):
        N = len(o.pop.people)
        # pot_haz = sum([covid_hazard(person.age) for person in o.pop.people])
        # tot_haz = sum([covid_hazard(person.age) for person in o.pop.infected()])
        if o.step_num == 1:
            # set up heatmap range with all population's coordinates
            self.heatmap_range = setup_range_for_histogram(o.pop)

        all_completed_tests = [t for q in o.society.queues for t in q.completed_tests]
        step = [o.time,
                o.pop.count_infected() / N,
                o.pop.count_infectious() / N,
                len(all_completed_tests) / N / o.time_increment,
                sum(len([t for t in q.tests if t.swab_taken]) for q in o.society.queues) / N,
                sum(p.isolating for p in o.pop.people) / N,
                # len([t for t in all_completed_tests if t.positive]) / N / o.time_increment,
                # tot_haz/pot_haz,
                ]
        # Increase the update frequency to have more heatmap images to show in video
        if o.step_num % (7 * o.society.episodes_per_day) == 1 or (o.step_num == o.n_periods):
            logging.info(f"Day {int(step[0])}, prop infected is {step[1]:2.2f}, "
                         f"prop infectious is {step[2]:2.4f}")
            # Generate heatmaps for infectious people along the time, feed heatmaps into camera
            if o.pop.count_infectious() > 0:
                coord = [[p.home.coordinate['lon'], p.home.coordinate['lat']] for p in o.pop.people if
                         p.infectious]
                coord_column_list = list(zip(*coord))
                # param range in np.histogram2d: The leftmost and rightmost edges of the bins along each dimension : [[xmin, xmax], [ymin, ymax]]
                # All values outside of this range will be considered outliers and not tallied in the histogram.
                heatmap, xedges, yedges = np.histogram2d(coord_column_list[0], coord_column_list[1], bins=300,\
                                                         range=[[self.heatmap_range[0], self.heatmap_range[1]],
                                                                [self.heatmap_range[2], self.heatmap_range[3]]])
               
                extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
                ax = plt.gca()
                ax.text(0.1, 1.02, f'Day {int(step[0])}, prop infectious is {step[2]:2.4f} in simulated Leeds', transform=ax.transAxes)
                plt.xlabel('latitude')
                plt.ylabel('longitude')
                plt.imshow(heatmap.T, extent=extent, origin='lower', vmin=0, vmax=20)
                self.camera.snap()
                
        self.story.append(step)

    def plot(self, **kwargs):
        df = self.get_dataframe()
        ax = (df.drop(columns=['ever infected']) * 100).plot(grid=True, **kwargs)
        ax.set_ylabel("percent of the population")
        logging.info(f" Realized R0 of early infections is {self.realized_r0:2.2f}")
        logging.info(f" {self.story[-1][1] * 100:2.1f} percent of the proportion was infected during the epidemic")

    def get_dataframe(self):
        df = pd.DataFrame(self.story)
        df.columns = ['days of epidemic', 'ever infected', 'infectious',
                      'tested daily', 'waiting for test results', 'isolating']  # , 'daily_detected_']
        df = df.set_index('days of epidemic')
        return df
