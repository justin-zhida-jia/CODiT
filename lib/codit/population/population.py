import random
from collections import defaultdict
from codit.population.person import Person
from codit.config import CFG

import numpy as np


class Population:
    def __init__(self, n_people, society, person_type=None):
        person_type = person_type or Person
        self.people = [person_type(society, config=society.cfg.__dict__, name=f"person {i}") for i in range(n_people)]

    def reset_people(self, society):
        for person in self.people:
            person.__init__(society, config=society.cfg.__dict__, name=person.name)

    def attack_in_groupings(self, group_size):
        groups = self.form_groupings(group_size)
        for g in groups:
            g = [p for p in g if not p.isolating]
            if len(g) < 2:
                continue
            for p1 in g:
                if p1.infectious:
                    days = 1. / p1.society.episodes_per_day
                    for p2 in g:
                        if p2 != p1:
                            p1.infectious_attack(p2, days=days)

    def form_groupings(self, group_size):
        return (random.sample(self.people, group_size) for _ in range(len(self.people)))

    def seed_infections(self, n_infected, disease, seed_periods=None):
        seed_periods = seed_periods or disease.days_infectious
        for p in random.sample(self.people, n_infected):
            p.set_infected(disease)
            stage = random.random() * seed_periods
            while p.days_infected() < stage:
                p.update_time()

    def count_infectious(self, disease=None):
        infected = self.infected(disease)
        return sum(p.infectious for p in infected)

    def count_infected(self, disease=None):
        return len(self.infected(disease))

    def infected(self, disease=None):
        if disease is None:
            return [p for p in self.people if p.immunities]
        return [p for p in self.people if (disease in p.immunities)]

    def update_time(self):
        for p in self.people:
            p.update_time()

    def victim_dict(self):
        """
        :return: a dictionary from infector to the tuple of people infected
        """
        return {person: person.victims for person in self.people if person.infected}

    def realized_r0(self, max_chain_len=4):
        """
        :return: We look at early infectees only.
        """
        n_victims = [len(person.victims) for person in self.people if
                     person.infector is not None and
                     len(person.chain()) <= max_chain_len]
        return np.mean(n_victims)


class FixedNetworkPopulation(Population):
    def __init__(self, n_people, society, person_type=None):
        Population.__init__(self, n_people, society, person_type=person_type)
        self.fixed_cliques = self.fix_cliques(society.encounter_size)
        self.contacts = self.find_contacts()

    def find_contacts(self):
        d = defaultdict(set)
        for gr_set in self.fixed_cliques:
            for p1 in gr_set:
                d[p1] |= gr_set
        for p in self.people:
            p.contacts = tuple(d[p] - {p})
        return {p: p.contacts for p in self.people}

    def fix_cliques(self, mean_num_contacts, group_size=2):
        n_groups = int((len(self.people) + 1) * mean_num_contacts / group_size)
        ii_jj = [random.choices(self.people, k=n_groups) for _ in range(group_size)]
        return [set(g) for g in zip(*ii_jj) if len(set(g)) == group_size]

    def form_groupings(self, group_size):
        """
        :param group_size: Does nothing in this method
        :return: So, people meet all their contacts on each round. If they have
        3 contacts on average, and a 1/3 chance of infecting one of them in a day,
         then they will infect on average one other each day.
        In our baseline config, this goes on for 2 days,
        after which they probably isolate.
        """
        for grp in self.fixed_cliques:
            yield grp