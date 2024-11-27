import random
import numpy as np
import itertools
import copy

from user.user import User 
from user.base_user import BaseUser

from simulator.base_simulator import BaseSimulator

def define_simulator(demographic_universe):
    pillars = ["Diet", "Physical Activity", "Smoking", "Alcohol", "Mental Wellbeing"]
    initial_pillar_prob_comb = generate_initial_pillar_prob_comb(demographic_universe, pillars)
    stay_prob = 0.8
    n_missions_per_HHS = 3
    mission_probabilities_comb = generate_mission_probabilities_comb(demographic_universe, pillars, n_missions_per_HHS)

    def get_mission_base_success_probability(self, pillar, mission):
        mission_base_success_probability = self.mission_probabilities[pillar][int(mission[0])]['probabilities'][int(mission[1])]
        return mission_base_success_probability

    def get_recommendation_success_probability(self, top_recommendation_boost, mission_base_success_probability, recommendation):
        age = self.demographic_profile[0]
        if age==recommendation:
            recommendation_boost = top_recommendation_boost
        else:
            recommendation_boost = 0
        return max(0, min(1, mission_base_success_probability + recommendation_boost))

    simulator = BaseSimulator(demographic_universe, pillars, initial_pillar_prob_comb, stay_prob, n_missions_per_HHS, mission_probabilities_comb, 
                            get_mission_base_success_probability, get_recommendation_success_probability)
    
    return simulator

def generate_base_users(n_users, demographic_universe, pillars, initial_pillars_prob_comb, stay_prob, n_missions_per_HHS, generate_mission_probabilities_comb):
    users = []
    print(f"Generating {n_users} users...")
    for _ in range(n_users):
        demographic_profile = generate_demographic_profile(demographic_universe)
        initial_pillars_prob = copy.deepcopy(initial_pillars_prob_comb[demographic_profile])
        mission_probabilities = copy.deepcopy(generate_mission_probabilities_comb[demographic_profile])
        # Generate random HHS scores (could be based on some distribution or predefined ranges)
        HHS = {
            "Diet": random.randint(0, 9),
            "Physical Activity": random.randint(0, 9),
            "Smoking": random.randint(0, 9),
            "Alcohol": random.randint(0, 9),
            "Mental Wellbeing": random.randint(0, 9)
        }

        # Create a User object with random demographics and the given params
        user = BaseUser(demographic_profile=demographic_profile,
                    pillars=pillars, initial_pillars_prob=initial_pillars_prob, 
                    HHS=HHS, stay_prob=stay_prob, 
                    n_missions_per_HHS=n_missions_per_HHS, mission_probabilities=mission_probabilities)
        users.append(user)
    
    print(f"Users generated.\n")
    
    return users


def generate_users(n_users, demographic_universe, pillars, initial_pillars_prob_comb, params, n_missions_per_HHS, generate_mission_probabilities_comb):
    users = []
    print(f"Generating {n_users} users...")
    for _ in range(n_users):
        demographic_profile = generate_demographic_profile(demographic_universe)
        initial_pillars_prob = copy.deepcopy(initial_pillars_prob_comb[demographic_profile])
        mission_probabilities = copy.deepcopy(generate_mission_probabilities_comb[demographic_profile])
        # Generate random HHS scores (could be based on some distribution or predefined ranges)
        HHS = {
            "Diet": random.randint(0, 9),
            "Physical Activity": random.randint(0, 9),
            "Smoking": random.randint(0, 9),
            "Alcohol": random.randint(0, 9),
            "Mental Wellbeing": random.randint(0, 9)
        }

        # Create a User object with random demographics and the given params
        user = User(demographic_profile=demographic_profile,
                    pillars=pillars, initial_pillars_prob=initial_pillars_prob, 
                    HHS=HHS, params=params, 
                    n_missions_per_HHS=n_missions_per_HHS, mission_probabilities=mission_probabilities)
        users.append(user)
    
    print(f"Users generated.\n")
    
    return users


def generate_demographic_profile(demographic_universe):
    demographic_profile = []
    i = 0
    for _, value in demographic_universe.items():
        demographic_profile.append(random.choice(value))
        i += 1
    return tuple(demographic_profile)


# Discretize Demography into Categories
def discretize_demography(self):
    # Discretize the age into categories: 0-20, 21-40, 41-60, 61+
    age_category = 0 if self.demography["age"] <= 20 else 1 if self.demography["age"] <= 40 else 2 if self.demography["age"] <= 60 else 3

    # Discretize socio_status into categories: Low, Medium, High
    socio_status_category = 0 if self.demography["socio_status"] == "low" else 1 if self.demography["socio_status"] == "medium" else 2
    
    # Discretize gender: Male=0, Female=1
    gender_category = 0 if self.demography["gender"] == "male" else 1

    # Discretize location: Urban=0, Rural=1
    location_category = 0 if self.demography["location"] == "urban" else 1

    # Create a tuple representing the demographic profile
    self.demographic_profile = (age_category, gender_category, location_category, socio_status_category)


def generate_initial_pillar_prob_comb(demographic_universe, pillars):
    demographic_combinations = list(itertools.product(*demographic_universe.values()))
    initial_pillar_prob_comb = {}

    # For each demographic combination, generate random probabilities for the pillars
    for combination in demographic_combinations:
        random_numbers = np.random.rand(len(pillars))        
        normalized_probabilities = random_numbers / np.sum(random_numbers)        
        initial_pillar_prob_comb[combination] = normalized_probabilities
    
    return initial_pillar_prob_comb


# Generate Mission Probabilities based on Demographic Profile, HHS, and Pillar
def generate_mission_probabilities_comb(demographic_universe, pillars, n_missions_per_HHS):
    # Resetting mission probabilities
    mission_probabilities_comb = {}

    # Define a grid of possible demographic combinations (age, gender, location, socio_status)
    demographic_combinations = list(itertools.product(*demographic_universe.values()))

    for profile in demographic_combinations:
        # Dictionary to hold mission probabilities for each pillar and HHS score
        profile_mission_probs = {}
        
        for pillar in pillars:
            pillar_probs = {}
            
            for HHS in range(10):  # For each HHS score (0 to 9)
                # Randomize mission probabilities for the current profile, pillar, and HHS score
                random_values = np.sort(np.random.rand(n_missions_per_HHS - 1))  # Sorted random breakpoints
                mission_probs = np.diff([0] + list(random_values) + [1])  # Compute lengths of segments

                # Store missions with probabilities (e.g., "00", "01", "02" for HHS = 0)
                pillar_probs[HHS] = {
                    "missions": [f"{HHS}{i}" for i in range(3)],
                    "probabilities": mission_probs
                }

            # Store the pillar's mission probabilities for this demographic profile
            profile_mission_probs[pillar] = pillar_probs
        
        # Store mission probabilities for the entire profile across all self.pillars
        mission_probabilities_comb[profile] = profile_mission_probs
    
    return mission_probabilities_comb


def get_mission_base_success_probability(demographic_profile, pillar, mission, mission_probabilities_comb):
    mission_base_success_probability = mission_probabilities_comb[demographic_profile][pillar][int(mission[0])]['probabilities'][int(mission[1])]
    return mission_base_success_probability


def get_recommendation_success_probability(demographic_profile, mission_base_success_probability, recommendation):
    age = demographic_profile[0]
    if age==recommendation:
        recommendation_boost = 0.5
    else:
        recommendation_boost = 0

    recommendation_success_probability = max(0, min(1, mission_base_success_probability + recommendation_boost))
    return recommendation_success_probability








# Create a function that calculates initial pillar selection probabilities based on D and HHS
def get_initial_pillar_probabilities(self):
    # Example logic: 
    # Age and socio_status might influence pillar probabilities, along with the user's HHS
    base_probabilities = np.array([self.params["k_base"], self.params["k_base"], self.params["k_base"], self.params["k_base"], self.params["k_base"]])  # Uniform probability for simplicity
    
    # Modify probabilities based on demographic factors and HHS
    if self.demography["age"] > 50:  # Older age may have different preferences (example)
        base_probabilities[4] += self.params["k_age"]  # Increase probability for Mental Wellbeing pillar
    if self.demography["socio_status"] == "high":  # High socio-status might impact activity levels
        base_probabilities[1] += self.params["k_socioeco"]  # Increase Physical Activity probability

    # Adjust probabilities based on HHS (e.g., higher HHS favors the behavior)
    for i, pillar in enumerate(self.pillars):
        base_probabilities[i] += self.HHS[pillar] * self.params["k_HHS"]  # Adjust based on HHS score

    # Normalize probabilities so they sum to 1
    base_probabilities = np.clip(base_probabilities, 0, 1)  # Ensure they are within [0, 1]
    base_probabilities /= np.sum(base_probabilities)  # Normalize to sum to 1

    self.pillar_probabilities = base_probabilities
    return self.pillar_probabilities





