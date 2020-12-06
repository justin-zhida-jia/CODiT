import sys
import os
import random
import numpy as np

# point at library; I need some lessons on doing good PYTHONPATHs:
REPO_DIR = os.path.dirname(os.getcwd())
sys.path.append(os.path.join(REPO_DIR, 'lib'))

from outbreak import Outbreak
from society import TestingTracingSociety
from society.alternatives import StrategicTester
from society.strategic import TwoTrackTester
from society.lateral import LateralFlowUK
from disease import Covid
from population.networks.radial_age import RadialAgePopulation
from population.networks.household_workplace import HouseholdWorkplacePopulation

ALL_TIME_DAYS = 15


def test_two_track_society():
    random.seed(42)
    o = Outbreak(TwoTrackTester(), Covid(), pop_size=5000, seed_size=50, n_days=150)
    o.simulate()


def test_two_track_hetero_society():
    random.seed(42)
    o = Outbreak(TwoTrackTester(), Covid(), pop_size=5000, seed_size=50, n_days=150,
                 population_type=RadialAgePopulation)
    o.simulate()


def test_two_track_hw_society():
    random.seed(42)
    o = Outbreak(TwoTrackTester(), Covid(), pop_size=5000, seed_size=50, n_days=150,
                 population_type=HouseholdWorkplacePopulation)
    o.simulate()


def test_smart_society():
    random.seed(42)
    o = Outbreak(StrategicTester(), Covid(), pop_size=5000, seed_size=50, n_days=150)
    o.simulate()


def test_covid_model():
    s = TestingTracingSociety(episodes_per_day=2, config=dict(PROB_TEST_IF_REQUESTED=0.4))
    random.seed(42)
    np.random.seed(42)
    o = Outbreak(s, Covid(), pop_size=8, seed_size=1, n_days=ALL_TIME_DAYS)
    o.simulate()
    # for k, v in o.pop.contacts.items():
    #     print(k, len(v))
    #                           t     cov   risks  tests  isol
    assert o.recorder.story[:15] == [[0.5, 0.25, 0.125, 0.0, 0.125, 0.0],
                                     [1.0, 0.25, 0.125, 0.25, 0.0, 0.0],
                                     [1.5, 0.25, 0.125, 0.0, 0.0, 0.0],
                                     [2.0, 0.375, 0.125, 0.0, 0.0, 0.0],
                                     [2.5, 0.375, 0.125, 0.0, 0.0, 0.0],
                                     [3.0, 0.375, 0.125, 0.0, 0.0, 0.0],
                                     [3.5, 0.375, 0.125, 0.0, 0.0, 0.0],
                                     [4.0, 0.375, 0.125, 0.0, 0.0, 0.125],
                                     [4.5, 0.375, 0.25, 0.0, 0.0, 0.125],
                                     [5.0, 0.5, 0.25, 0.0, 0.0, 0.125],
                                     [5.5, 0.5, 0.125, 0.0, 0.0, 0.125],
                                     [6.0, 0.5, 0.25, 0.0, 0.0, 0.125],
                                     [6.5, 0.5, 0.25, 0.0, 0.0, 0.125],
                                     [7.0, 0.5, 0.25, 0.0, 0.0, 0.125],
                                     [7.5, 0.5, 0.25, 0.0, 0.0, 0.125]]
