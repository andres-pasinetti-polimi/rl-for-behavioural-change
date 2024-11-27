import copy
import random

from user.base_user import BaseUser

# Define the Demography for a User
class BaseSimulator:
    def __init__(self, demographic_universe, pillars, initial_pillars_prob_comb, stay_prob, n_missions_per_HHS, mission_probabilities_comb, 
                 get_mission_base_success_probability, get_recommendation_success_probability):
        self.demographic_universe = demographic_universe 
        self.pillars = pillars
        self.initial_pillars_prob_comb = initial_pillars_prob_comb
        self.stay_prob = stay_prob
        self.n_missions_per_HHS = n_missions_per_HHS
        self.mission_probabilities_comb = mission_probabilities_comb
        self.get_mission_base_success_probability = get_mission_base_success_probability
        self.get_recommendation_success_probability = get_recommendation_success_probability


    def generate_users(self, n_users):
        users = []
        for _ in range(n_users):
            demographic_profile = self.sample_demographic_profile()
            initial_pillars_prob = copy.deepcopy(self.initial_pillars_prob_comb[demographic_profile])
            # Generate random HHS scores
            HHS = {
                "Diet": random.randint(0, 9),
                "Physical Activity": random.randint(0, 9),
                "Smoking": random.randint(0, 9),
                "Alcohol": random.randint(0, 9),
                "Mental Wellbeing": random.randint(0, 9)
            }
            mission_probabilities = copy.deepcopy(self.mission_probabilities_comb[demographic_profile])
            user = BaseUser(demographic_profile=demographic_profile,
                        pillars=self.pillars, initial_pillars_prob=initial_pillars_prob, 
                        HHS=HHS, stay_prob=self.stay_prob, 
                        n_missions_per_HHS=self.n_missions_per_HHS, mission_probabilities=mission_probabilities,
                        get_mission_base_success_probability=self.get_mission_base_success_probability,
                        get_recommendation_success_probability=self.get_recommendation_success_probability)
            users.append(user)
        return users
    

    def sample_demographic_profile(self):
        demographic_profile = []
        i = 0
        for _, value in self.demographic_universe.items():
            demographic_profile.append(random.choice(value))
            i += 1
        return tuple(demographic_profile)