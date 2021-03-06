import random
import numpy as np

from codit.outbreak import Outbreak
from codit.society import TestingTracingSociety, ContactTestingSociety
from codit.society.strategic import TwoTrackTester
from codit.disease import Covid

ALL_TIME_DAYS = 15


def test_covid_model():
    s = TestingTracingSociety(episodes_per_day=2, config=dict(PROB_TEST_IF_REQUESTED=0.4))
    random.seed(42)
    np.random.seed(42)
    o = Outbreak(s, Covid(), pop_size=8, seed_size=1, n_days=ALL_TIME_DAYS)
    o.simulate()
    # for k, v in o.pop.contacts.items():
    #     print(k, len(v))
    #                                 t     cov   risks  tests  isol
    np.testing.assert_allclose(o.recorder.story[:15], [[0.5, 0.25, 0.125, 0.0, 0.125, 0.0],
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
                                                       [7.5, 0.5, 0.25, 0.0, 0.0, 0.125]])


def test_contact_testing():
    s = ContactTestingSociety(episodes_per_day=2)
    random.seed(42)
    np.random.seed(42)
    o = Outbreak(s, Covid(), pop_size=8, seed_size=1, n_days=ALL_TIME_DAYS)
    o.simulate()
    # for k, v in o.pop.contacts.items():
    #     print(k, len(v))
    #                                 t     cov   risks  tests  isol
    np.testing.assert_allclose(o.recorder.story[:15], [[0.5, 0.25, 0.125, 0.0, 0.125, 0.0],
                                                       [1.0, 0.25, 0.125, 0.0, 0.125, 0.0],
                                                       [1.5, 0.25, 0.125, 0.0, 0.125, 0.0],
                                                       [2.0, 0.25, 0.125, 0.0, 0.125, 0.0],
                                                       [2.5, 0.25, 0.125, 0.0, 0.125, 0.0],
                                                       [3.0, 0.25, 0.125, 0.0, 0.125, 0.0],
                                                       [3.5, 0.25, 0.125, 0.0, 0.125, 0.0],
                                                       [4.0, 0.25, 0.125, 0.0, 0.125, 0.125],
                                                       [4.5, 0.25, 0.25, 0.0, 0.125, 0.125],
                                                       [5.0, 0.375, 0.25, 0.0, 0.125, 0.125],
                                                       [5.5, 0.375, 0.125, 0.0, 0.125, 0.125],
                                                       [6.0, 0.375, 0.125, 0.0, 0.125, 0.125],
                                                       [6.5, 0.375, 0.125, 0.0, 0.125, 0.125],
                                                       [7.0, 0.375, 0.125, 0.0, 0.125, 0.125],
                                                       [7.5, 0.375, 0.125, 0.0, 0.125, 0.125]])


def test_two_track_model():
    s = TwoTrackTester(episodes_per_day=2)
    random.seed(42)
    np.random.seed(42)
    o = Outbreak(s, Covid(), pop_size=8, seed_size=1, n_days=ALL_TIME_DAYS)
    o.simulate()
    # for k, v in o.pop.contacts.items():
    #     print(k, len(v))
    #                                 t     cov   risks  tests tests_back  isol
    np.testing.assert_allclose(o.recorder.story[:15], [[0.5, 0.25, 0.125, 0.0, 0.125, 0.0],
                                                       [1.0, 0.25, 0.125, 0.0, 0.125, 0.0],
                                                       [1.5, 0.25, 0.125, 0.0, 0.125, 0.0],
                                                       [2.0, 0.25, 0.125, 0.0, 0.125, 0.0],
                                                       [2.5, 0.25, 0.125, 0.0, 0.125, 0.0],
                                                       [3.0, 0.25, 0.125, 0.0, 0.125, 0.0],
                                                       [3.5, 0.25, 0.125, 0.0, 0.125, 0.0],
                                                       [4.0, 0.375, 0.125, 0.0, 0.125, 0.0],
                                                       [4.5, 0.375, 0.25, 0.0, 0.125, 0.0],
                                                       [5.0, 0.5, 0.25, 0.0, 0.125, 0.0],
                                                       [5.5, 0.5, 0.125, 0.0, 0.125, 0.0],
                                                       [6.0, 0.5, 0.125, 0.0, 0.125, 0.0],
                                                       [6.5, 0.5, 0.125, 0.0, 0.125, 0.0],
                                                       [7.0, 0.5, 0.125, 0.0, 0.125, 0.0],
                                                       [7.5, 0.5, 0.125, 0.0, 0.125, 0.0]])
