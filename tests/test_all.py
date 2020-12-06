import sys
import os
import random

# point at library; I need some lessons on doing good PYTHONPATHs:
REPO_DIR = os.path.dirname(os.getcwd())
sys.path.append(os.path.join(REPO_DIR, 'lib'))

from society import Society
from disease import Disease
from outbreak import Outbreak
from population import Population
from population.person import Person

ALL_TIME_DAYS = 50


def test_uk_ovespill_model():
    from society.alternatives import UKSociety
    from disease import Covid
    random.seed(42)
    o = Outbreak(UKSociety(config=dict(PROB_NON_C19_SYMPTOMS_PER_DAY=0.1)),
                 Covid(), pop_size=1000, seed_size=20, n_days=ALL_TIME_DAYS)
    o.simulate()
    assert o.recorder.story[40:45] == [[41.0, 0.035, 0.0, 0.007, 0.467, 0.452],
                                       [42.0, 0.035, 0.0, 0.007, 0.458, 0.442],
                                       [43.0, 0.035, 0.0, 0.007, 0.461, 0.447],
                                       [44.0, 0.035, 0.0, 0.007, 0.458, 0.448],
                                       [45.0, 0.035, 0.0, 0.007, 0.457, 0.448]]


def test_covid_model():
    from society import TestingSociety
    from disease import Covid
    s = TestingSociety(episodes_per_day=5, config={ "MEAN_NETWORK_SIZE": 2,
                                                    "PROB_NON_C19_SYMPTOMS_PER_DAY": 0,
                                                    "PROB_TEST_IF_REQUESTED": 0.4})

    d = Covid(days_infectious=10, pr_transmission_per_day=0.2)
    # seed size is the number of people in the population who we seed as being infected:
    random.seed(42)
    o = Outbreak(s, d, pop_size=1000, seed_size=20, n_days=ALL_TIME_DAYS)
    # so, this is a village of 10000 people with 2 starting off infected

    random.seed(42)
    o.simulate()
    assert o.recorder.story[90:95] == \
           [[18.199999999999967, 0.103, 0.044, 0.0, 0.0, 0.023],
            [18.399999999999967, 0.103, 0.046, 0.0, 0.0, 0.023],
            [18.599999999999966, 0.103, 0.045, 0.0, 0.0, 0.021],
            [18.799999999999965, 0.105, 0.043, 0.0, 0.0, 0.019],
            [18.999999999999964, 0.105, 0.043, 0.0, 0.0, 0.017]]
"""
Day 9, prop infected is 0.061, prop infectious is 0.061
Day 19, prop infected is 0.141, prop infectious is 0.08
Day 29, prop infected is 0.226, prop infectious is 0.085
Day 40, prop infected is 0.294, prop infectious is 0.068
Day 50, prop infected is 0.34, prop infectious is 0.046
"""



def test_draconian_population_model():
    from society.basic import DraconianSociety
    random.seed(42)
    s = DraconianSociety(episodes_per_day=5, encounter_size=2)
    d = Disease(days_infectious=10, pr_transmission_per_day=0.2)
    # seed size is the number of people in the population who we seed as being infected:
    o = Outbreak(s, d, pop_size=1000, seed_size=2, n_days=ALL_TIME_DAYS, population_type=Population, person_type=Person)
    # so, this is a village of 10000 people with 2 starting off infected
    o.simulate()
    assert o.recorder.story[90:95] == \
           [[18.199999999999967, 0.002, 0.0, 0.0, 0.0, 0.0],
            [18.399999999999967, 0.002, 0.0, 0.0, 0.0, 0.0],
            [18.599999999999966, 0.002, 0.0, 0.0, 0.0, 0.0],
            [18.799999999999965, 0.002, 0.0, 0.0, 0.0, 0.0],
            [18.999999999999964, 0.002, 0.0, 0.0, 0.0, 0.0]]


def test_toy_model():
    random.seed(42)
    s = Society(episodes_per_day=5, encounter_size=2)
    d = Disease(days_infectious=10, pr_transmission_per_day=0.2)
    # seed size is the number of people in the population who we seed as being infected:
    o = Outbreak(s, d, pop_size=1000, seed_size=2, n_days=ALL_TIME_DAYS, population_type=Population, person_type=Person)
    # so, this is a village of 10000 people with 2 starting off infected
    o.simulate()
    assert o.recorder.story[90:95] == \
           [[18.199999999999967, 0.619, 0.57, 0.0, 0.0, 0.0],
            [18.399999999999967, 0.643, 0.592, 0.0, 0.0, 0.0],
            [18.599999999999966, 0.656, 0.603, 0.0, 0.0, 0.0],
            [18.799999999999965, 0.673, 0.618, 0.0, 0.0, 0.0],
            [18.999999999999964, 0.69, 0.635, 0.0, 0.0, 0.0]]
