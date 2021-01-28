import random
import numpy as np
import logging

from codit.population.population import FixedNetworkPopulation
from codit.population.networks import household_workplace
from codit.population.networks.city_config.city_cfg import MINIMUM_WORKING_AGE, MAXIMUM_WORKING_AGE, MAXIMUM_CLASS_AGE, MINIMUM_CLASS_AGE, AVERAGE_HOUSEHOLD_SIZE
from codit.population.networks.city_config.typical_households import build_characteristic_households
# Import home module
from codit.population.networks import home
from codit.population.networks.home import Home, COORDINATES_CSV, TYPES_CONSTRAINTS_CSV

EPHEMERAL_CONTACT = 0.1  # people per day


class CityPopulation(FixedNetworkPopulation):
    def reset_people(self, society):
        """
        Override reset_people() to allow the new attribute person.home in CityPopulation can be saved when reset the
        population according to different type of society
        :param society:
        :return:
        """
        # logging.info("CityPopulation.reset_people")
        # count = 0
        for person in self.people:
            # if count < 5:
            # logging.info(f"reset person's home to {person.home.type}, {person.home.coordinate['lon']} and {person.home.coordinate['lat']}")
            # count += 1
            person.__init__(society, config=society.cfg.__dict__, name=person.name, home=person.home)

    def fix_cliques(self, encounter_size):
        """
        :param encounter_size: not used
        :return:
        """
        static_cliques = self.build_city_cliques()
        logging.info(f"Adding {len(static_cliques)} permanent contact groups")
        dynamic_cliques = FixedNetworkPopulation.fix_cliques(self, EPHEMERAL_CONTACT)
        logging.info(f"Adding {len(dynamic_cliques)} ephemeral contact pairs")
        return static_cliques + dynamic_cliques


    def build_city_cliques(self):
        """
        Change it to a class method to make sure the Home attribute assigned to person can be saved in self.people

        :return: a list of little sets, each is a 'clique' in the graph, some are households, some are workplaces
        each individual should belong to exactly one household and one workplace
        for example: [{person_0, person_1, person_2}, {person_0, person_10, person_54, person_88, person_550, person_270}]
        - except not everyone is accounted for of course
        """
        households = self.build_households()
        report_size(households, 'households')

        classrooms = build_class_groups(self.people)

        working_age_people = [p for p in self.people if MINIMUM_WORKING_AGE < p.age < MAXIMUM_WORKING_AGE]
        teachers = random.sample(working_age_people, len(classrooms))
        classrooms = [clss | {teachers[i]} for i, clss in enumerate(classrooms)]
        report_size(classrooms, 'classrooms')

        care_homes = [h for h in households if is_care_home(h)]
        carers = assign_staff(care_homes, working_age_people)

        working_age_people = list(set(working_age_people) - set(teachers) - set(carers))
        random.shuffle(working_age_people)
        workplaces = build_workplaces(working_age_people)
        report_size(workplaces, 'workplaces')

        return households + workplaces + classrooms + care_homes

    def build_households(self):
        """
        Change it to a class method to make sure the Home attribute assigned to person can be saved in self.people

        :return: a list of households, where households are a list of person objects. now with an assigned age.
        """
        n_individuals = len(self.people)
        assigned = 0
        households = []
        # to recycle allocated homes whose type is either 'apartment' or 'terrace'
        allocated_coordinates_list = []

        num_h = int(n_individuals / AVERAGE_HOUSEHOLD_SIZE)
        household_examples = build_characteristic_households(num_h)
        # create num_h of homes
        homes_list = build_households_home_list(num_h)
        logging.info(f"There are {len(homes_list)} households generated for accommodation buildings")

        while assigned < n_individuals:
            ages = next_household_ages(household_examples)
            size = len(ages)
            # randomly pick up a home from list of homes
            home = next_household_home(homes_list, allocated_coordinates_list)

            if assigned + size > n_individuals:
                ages = ages[:n_individuals - assigned - size]
                size = len(ages)

            hh = []
            for j, age in enumerate(ages):
                indiv = self.people[j + assigned]
                indiv.age = age
                # Initiate Home instance with (coordinates and building_type) to each person's home attribute within the population
                self.people[j + assigned].home = Home(home[0], home[1], home[2])

                hh.append(indiv)
            households.append(set(hh))
            assigned += size

        return households


def is_care_home(home):
    return min([p.age for p in home]) >= MAXIMUM_WORKING_AGE and len(home) > 20


def assign_staff(care_homes, working_age_people, staff=5):
    carers = set()
    for home in care_homes:
        home_carers = set(random.sample(working_age_people, staff))
        home |= home_carers
        carers |= home_carers
    report_size(care_homes, 'care_homes')
    return carers


def report_size(care_homes, ch):
    logging.info(f"{len(care_homes)} {ch} of mean size {np.mean([len(x) for x in care_homes]):2.2f}")


def build_class_groups(people):
    classrooms = []
    for kids_age in range(MINIMUM_CLASS_AGE, MAXIMUM_CLASS_AGE+1):
        schoolkids = [p for p in people if p.age == kids_age]
        random.shuffle(schoolkids)
        classrooms += build_workplaces(schoolkids, classroom_size=30)
    logging.info(f"Only putting children >{MINIMUM_CLASS_AGE} years old into classrooms.")
    return classrooms

def build_households_home_list(total_h=50000):
    """
    Build a list of total_h households: ['lon', 'lat', 'building_type']
    :param total_h: total number of households
    :return: a full list of ['lon', 'lat', 'building_type']
    """
    coords_types = home.get_coords(COORDINATES_CSV)
    types_counts = home.count_coords_for_types(coords_types)
    df_types_constraints_households = home.merge_building_types_constraints_to_accommodations(types_counts, TYPES_CONSTRAINTS_CSV)

    aver_num_households = (df_types_constraints_households['min_households'] + df_types_constraints_households['max_households']) / 2
    df_types_constraints_households['average_num_households'] = aver_num_households
    init_total_households = np.sum(df_types_constraints_households['number'] * aver_num_households)
    index_apartments = df_types_constraints_households['building_type']=='apartments'
    remaining_households_in_apartments = total_h - (init_total_households - df_types_constraints_households.loc[index_apartments, 'average_num_households'] * \
    df_types_constraints_households.loc[index_apartments, 'number'])
    df_types_constraints_households.loc[index_apartments, 'average_num_households'] = remaining_households_in_apartments / \
                                                                                        df_types_constraints_households.loc[index_apartments, 'number']
    df_types_constraints_households.drop('max_households', axis = 1, inplace=True)

    list_types_average_households = list(
        zip(df_types_constraints_households['building_type'], df_types_constraints_households['number'],
            df_types_constraints_households['average_num_households'] - df_types_constraints_households['min_households'],
            df_types_constraints_households['min_households']))
    list_num_households_per_building = home.allocate_households_to_each_building(total_h, list_types_average_households, coords_types)
    list_households_info = []
    for num_households_per_building in list_num_households_per_building:

        if int(num_households_per_building[3]) > 0:
            list_households_info += [num_households_per_building[:3]] * int(num_households_per_building[3])

    return list_households_info


def next_household_home(homes_list, allocated_coordinates_list):
    """
    Randomly pick up one home with ['lon', 'lat', 'building_type'], and remove the allocated home from the list,
    as the number of homes are pre-defined according to actual number of accommodation of buildings and average number of
    households per building_type, the actual number of households may exceed the pre-defined number of homes.
    So here we recycle the apartments and terraces homes to allocate again just in case, as these two building types can
    have multiple households.
    :param homes_list:
    :param allocated_coordinates_list:
    :return: one home ['lon', 'lat', 'building_type']
    """
    if len(homes_list) > 0:
        next_home = random.choice(homes_list)
        if next_home[2] == 'apartments' or next_home[2] == 'terrace':
            allocated_coordinates_list.append(next_home)
        homes_list.remove(next_home)
    else:
        next_home = random.choice(allocated_coordinates_list)
    return next_home

def next_household_ages(household_list):
    """
    :param: complete list of households
    :return: randomly select a type of household from a distribution suitable to City,
    and return the list of the ages of the people in that household
    """
    return random.choice(household_list)


def build_workplaces(people, classroom_size=-1):
    """
    :param people: lets for now let these be a list of N population.covid.PersonCovid() objects
    :return: a list of workplaces, where workplaces are a list of person objects.
    """
    n_individuals = len(people)
    assigned = 0
    workplaces = []
    while assigned < n_individuals:
        if classroom_size > 0:
            size = 30
        else:
            size = next_workplace_size()

        if assigned + size >= n_individuals:
            size = n_individuals - assigned

        assert size > 0

        hh = people[assigned: assigned + size]
        workplaces.append(set(hh))
        assigned += size

    return workplaces


def next_workplace_size():
    return random.choice(household_workplace.WORKPLACE_SIZE_REPRESENTATIVE_EXAMPLES)
