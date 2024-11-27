import numpy as np
import matplotlib.pyplot as plt
import types

# Define the Demography for a User
class BaseUser:
    def __init__(self, demographic_profile, pillars, initial_pillars_prob, HHS, stay_prob, n_missions_per_HHS, mission_probabilities, 
                 get_mission_base_success_probability, get_recommendation_success_probability):
        self.stay_prob = stay_prob
        self.demography = None
        self.pillars = pillars
        self.HHS = HHS  # Health Habit Scores (one per pillar)
        self.n_missions_per_HHS = n_missions_per_HHS
        self.mission_probabilities = mission_probabilities
        self.HHS_progress = {pillar: [self.HHS[pillar]] for pillar in self.pillars}
        self.initial_pillars_prob = initial_pillars_prob  # Probability for each pillar
        self.demographic_profile = demographic_profile  # Profile ID for the current user
        self.previous_pillar = None  # Track the previously selected pillar
        self.pillar_selection_history = []
        self.weeks = None
        #self.discretize_demography()
        self.get_mission_base_success_probability = get_mission_base_success_probability.__get__(self)
        self.get_recommendation_success_probability = get_recommendation_success_probability.__get__(self)


    def select_pillar(self, verbose=False):
        if self.previous_pillar is None:
            # Set probability to 0 for self.pillars with HHS = 9
            for i, pillar in enumerate(self.pillars):
                if self.HHS[pillar] == 9:
                    self.initial_pillars_prob[i] = 0
            
            # Normalize probabilities so they sum to 1 (ignoring zero probabilities)
            self.initial_pillars_prob = np.clip(self.initial_pillars_prob, 0, 1)  # Ensure they are within [0, 1]
            if np.sum(self.initial_pillars_prob) > 0:
                self.initial_pillars_prob /= np.sum(self.initial_pillars_prob)  # Normalize to sum to 1
            else:
                # If all self.pillars have an HHS of 9, set all probabilities to 0
                return None
            
            if verbose: print(np.round(self.initial_pillars_prob, 2))
            selected_pillar = np.random.choice(self.pillars, p=self.initial_pillars_prob)
        else:
            # If there is a previous pillar selected, handle the logic with 80% repeat, 20% switch
            if self.HHS[self.previous_pillar] < 9:
                # stay_prob chance of selecting the previous pillar, 1-stay_prob chance of switching
                available_pillars = [p for p in self.pillars if p != self.previous_pillar and self.HHS[p] != 9]
                transition_probabilities = [self.stay_prob if p == self.previous_pillar 
                                            else (1 - self.stay_prob) / (len(available_pillars)) if self.HHS[p]!= 9
                                            else 0 
                                            for p in self.pillars]
                transition_probabilities = [tp / sum(transition_probabilities) for tp in transition_probabilities]

                if verbose: print(np.round(transition_probabilities, 2))
                selected_pillar = np.random.choice(self.pillars, p=transition_probabilities)
            else:
                # If previous pillar reached max score (HHS = 9), we should adjust probabilities accordingly
                available_pillars = [p for p in self.pillars if self.HHS[p] != 9]
                if len(available_pillars)==0:
                    return None
                
                transition_probabilities = [0 if self.HHS[p]==9 else 1 / (len(available_pillars)) for p in self.pillars]
                transition_probabilities = [tp / sum(transition_probabilities) for tp in transition_probabilities]
            
                if verbose: print(np.round(transition_probabilities, 2))
                selected_pillar = np.random.choice(self.pillars, p=transition_probabilities)
        
        # Update the previous pillar selection
        self.previous_pillar = selected_pillar
        self.pillar_selection_history.append(selected_pillar)
        return selected_pillar
    

    # Select a mission based on the demographic profile, current HHS score, and pillar
    def select_mission(self, pillar, verbose=False):
        current_HHS = self.HHS[pillar]  # Get the current HHS score for the selected pillar
        
        # Select the mission probabilities based on the user's demographic profile and pillar
        profile_pillar_probs = self.mission_probabilities[pillar]
        available_missions = profile_pillar_probs[current_HHS]["missions"]
        mission_probs = profile_pillar_probs[current_HHS]["probabilities"]
        
        if verbose:
            print("Mission Selection Probabilities:", np.round(mission_probs, 2))
                    
        # Randomly select a mission based on the mission probabilities
        selected_mission = np.random.choice(available_missions, p=mission_probs)
        
        # Probability of successfully completing the mission
        mission_base_success_probability = self.get_mission_base_success_probability(pillar, selected_mission)
        return selected_mission, mission_base_success_probability


    def run_mission_loop(self, weeks=12, verbose=False):
        self.weeks=weeks
        for week in range(weeks):
            # Select a pillar based on previous selection (80% repeat)
            selected_pillar = self.select_pillar(verbose=verbose)
            if verbose:
                print(f"Week {week + 1}: Selected Pillar {selected_pillar}")
            
            # Select a mission within the chosen pillar and determine success probability
            selected_mission, success_probability = self.select_mission(selected_pillar, verbose=verbose)
            if verbose:
                print(f"Mission {selected_mission} selected for {selected_pillar} with Success Probability {success_probability:.2f}")
            
            # Determine success and update HHS if successful
            if np.random.rand() < success_probability:
                if verbose:
                    print(f"Mission {selected_mission} succeeded!")
                self.HHS[selected_pillar] = min(self.HHS[selected_pillar] + 1, 10)
            else:
                if verbose:
                    print(f"Mission {selected_mission} failed.")
            
            # Record the HHS for each pillar at the end of each week
            for pillar, HHS_score in self.HHS.items():
                self.HHS_progress[pillar].append(HHS_score)
            if verbose:
                print(f"User HHS: {self.HHS}")
                print("-" * 40)

            # Check if all values in the HHS dictionary are 9
            all_values_are_9 = all(value == 9 for value in self.HHS.values())

            if all_values_are_9:
                self.weeks = week+1
                break

    def plot_progress(self):
        # Create the plot
        plt.figure(figsize=(6, 3))

        # Plot the HHS progress over time for each pillar
        for pillar, scores in self.HHS_progress.items():
            # Plot each pillar with points at each week
            plt.plot(range(1, self.weeks+2), scores, label=pillar, marker='o', markersize=6, alpha=0.6)

        # Highlight the selected pillar for each week by coloring the entire week
        for week in range(1, self.weeks+1):
            selected_pillar = self.pillar_selection_history[week-1]  # Get the selected pillar for this week
            # Get the color of the selected pillar's line
            selected_color = plt.gca().lines[list(self.HHS_progress.keys()).index(selected_pillar)].get_color()
            # Color the entire week for the selected pillar
            plt.axvspan(week, week + 1, color=selected_color, alpha=0.2, zorder=-1)

        # Customize the plot
        plt.xlabel("Week")
        plt.ylabel("Health Habit Score (HHS)")
        plt.title("Pillar Health Habit Score Progress Over 12 Weeks")
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')  # Place legend outside on the right
        plt.xticks(range(1, self.weeks+1))  # One tick for each week
        plt.yticks(range(0, 10))  # One tick for each HHS
        plt.xlim(1, self.weeks+1)
        plt.ylim(-1, 10)
        plt.grid(True)
        plt.tight_layout()  # Ensure everything fits without clipping
        plt.show()



