import numpy as np

class ThompsonSamplingCMAB:
    def __init__(self, n_actions: int, n_contexts: int, alpha: float = 1.0, beta: float = 1.0):
        """
        Thompson Sampling for Contextual Multi-Armed Bandit (CMAB).
        
        Parameters:
            n_actions (int): The number of possible actions.
            n_contexts (int): The number of distinct contexts (e.g., age groups).
            alpha (float): The prior parameter for the Beta distribution (successes).
            beta (float): The prior parameter for the Beta distribution (failures).
        """
        self.n_actions = n_actions
        self.n_contexts = n_contexts
        
        # Successes and failures for each action-context pair
        self.successes = np.full((n_actions, n_contexts), alpha)
        self.failures = np.full((n_actions, n_contexts), beta)

    def select_action(self, context: int) -> int:
        """
        Select an action using Thompson Sampling.
        
        Parameters:
            context (int): The current context (e.g., user's age group).
        
        Returns:
            int: The action selected by Thompson Sampling.
        """
        # Sample from the posterior distribution (Beta distribution) for each action
        sampled_rewards = np.random.beta(self.successes[:, context], self.failures[:, context])
        
        # Select the action with the highest sampled reward
        return np.argmax(sampled_rewards)

    def update(self, context: int, action: int, reward: float):
        """
        Update the posterior distribution based on the observed reward.
        
        Parameters:
            context (int): The context (e.g., user's age group).
            action (int): The action taken.
            reward (float): The observed reward (binary, e.g., 0 or 1).
        """
        if reward == 1:
            self.successes[action, context] += 1
        else:
            self.failures[action, context] += 1