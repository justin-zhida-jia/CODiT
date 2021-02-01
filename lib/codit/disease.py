import logging

from codit.config import set_config


def covid_hazard(age):
    #  https://www.nature.com/articles/s41586-020-2521-4/tables/2
    if age > 80:
        return 38.29
    if age > 70:
        return 8.63
    if age > 60:
        return 2.79
    if age > 50:
        return 1.00
    if age > 40:
        return 0.28
    if age > 18:
        return 0.05
    return 0


def set_infectivity(covid_name, pr_transmission_per_day):
    """
    :param covid_name:
    :param pr_transmission_per_day:
    :return: we're keen to handle two cases: pr_transmission_per_day is a float, and pr_transmission_per_day is a dict
    """
    if type(pr_transmission_per_day) == dict:
        return pr_transmission_per_day[covid_name]
    return pr_transmission_per_day


class Disease:
    """
    This is not a case of a disease, it is the strain of disease.
    """
    def __init__(self, days_infectious, pr_transmission_per_day, covid_name=None, config=None):
        # TODO: would this be self.name rather than self.covid_name?
        set_config(self, config)
        self.days_infectious = days_infectious
        self.pr_transmit_per_day = set_infectivity(covid_name, pr_transmission_per_day)
        self.covid_name = covid_name

    def __repr__(self):
        return self.covid_name


class Covid(Disease):
    def __init__(self, days_infectious=None, pr_transmission_per_day=None, covid_name=None, config=None):
        set_config(self, config)
        days_infectious = days_infectious or (self.cfg.DAYS_INFECTIOUS_TO_SYMPTOMS + self.cfg.DAYS_OF_SYMPTOMS)
        pr_transmission_per_day = pr_transmission_per_day or self.cfg.PROB_INFECT_IF_TOGETHER_ON_A_DAY
        covid_name = covid_name or self.cfg.DEFAULT_COVID
        Disease.__init__(self, days_infectious, pr_transmission_per_day, covid_name)
        self.days_before_infectious = self.cfg.DAYS_BEFORE_INFECTIOUS
        self.days_to_symptoms = self.cfg.DAYS_INFECTIOUS_TO_SYMPTOMS
        self.prob_symptomatic = self.cfg.PROB_SYMPTOMATIC

        # when you stop showing symptoms, you stop being infectious
        self.days_of_symptoms = days_infectious - self.days_to_symptoms
        if self.cfg.DAYS_OF_SYMPTOMS != self.days_of_symptoms:
            logging.info(f"setting days of symptoms to {self.days_of_symptoms} rather than {self.cfg.DAYS_OF_SYMPTOMS}")

class Covid_Mutation(Covid):
    def __init__(self, pr_transmission_per_day=None, covid_name=None, config=None):
        Covid.__init__(self, pr_transmission_per_day=pr_transmission_per_day, covid_name=covid_name, config=config)
