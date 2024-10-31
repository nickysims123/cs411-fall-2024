import logging
from typing import List

from meal_max.models.kitchen_model import Meal, update_meal_stats
from meal_max.utils.logger import configure_logger
from meal_max.utils.random_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class BattleModel:
    """
<<<<<<< HEAD
    A class to conduct a battle between multiple meals.

    Attributes: 
        combatants (List[Meal]): List of meals currently battling.

=======
    A class used to manage the battle between meals

    Attributes:
        combatants (List[Meal]): Stores the list of combatants.
>>>>>>> f7dfcc7d2e0018a70890860b121e5b175fecb00d
    """

    def __init__(self):
        """
<<<<<<< HEAD
        Initializes the BattleModel with an empty combatants list.
=======
        Initializes the BattleModel with an empty list of combatants.
>>>>>>> f7dfcc7d2e0018a70890860b121e5b175fecb00d
        """
        self.combatants: List[Meal] = []

    def battle(self) -> str:
        """
<<<<<<< HEAD
        Conducts a battle between two combatants, displaying the winner and removing the loser.
        
        Raises:
            ValueError: If the battle does not enough combatants.

        Side-effects: 
            Updates meal stats for both combatants as win or loss accordingly.

        Returns:
            Combatant 1 or 2, depending on who won.
                
=======
        Starts battle between two combatants to determine a winner by calculating the battle score for each combatant, 
        comparing them with a random number, and determining the winner based on the delta. The winner remains in the list 
        while the loser gets removed.

        Returns:
            str: The name of the winning meal.

        Raises:
            ValueError: If there are less than two combatants.
>>>>>>> f7dfcc7d2e0018a70890860b121e5b175fecb00d
        """
        logger.info("Two meals enter, one meal leaves!")

        if len(self.combatants) < 2:
            logger.error("Not enough combatants to start a battle.")
            raise ValueError("Two combatants must be prepped for a battle.")

        combatant_1 = self.combatants[0]
        combatant_2 = self.combatants[1]

        # Log the start of the battle
        logger.info("Battle started between %s and %s", combatant_1.meal, combatant_2.meal)

        # Get battle scores for both combatants
        score_1 = self.get_battle_score(combatant_1)
        score_2 = self.get_battle_score(combatant_2)

        # Log the scores for both combatants
        logger.info("Score for %s: %.3f", combatant_1.meal, score_1)
        logger.info("Score for %s: %.3f", combatant_2.meal, score_2)

        # Compute the delta and normalize between 0 and 1
        delta = abs(score_1 - score_2) / 100

        # Log the delta and normalized delta
        logger.info("Delta between scores: %.3f", delta)

        # Get random number from random.org
        random_number = get_random()

        # Log the random number
        logger.info("Random number from random.org: %.3f", random_number)

        # Determine the winner based on the normalized delta
        if delta > random_number:
            winner = combatant_1
            loser = combatant_2
        else:
            winner = combatant_2
            loser = combatant_1

        # Log the winner
        logger.info("The winner is: %s", winner.meal)

        # Update stats for both combatants
        update_meal_stats(winner.id, 'win')
        update_meal_stats(loser.id, 'loss')

        # Remove the losing combatant from combatants
        self.combatants.remove(loser)

        return winner.meal

    def clear_combatants(self):
        """
<<<<<<< HEAD
        Clears the current battle of all combatants
=======
        Clears the current combatants from the battle list.
>>>>>>> f7dfcc7d2e0018a70890860b121e5b175fecb00d
        """
        logger.info("Clearing the combatants list.")
        self.combatants.clear()

    def get_battle_score(self, combatant: Meal) -> float:
        """
<<<<<<< HEAD
        Gets the battle scores of a combatant based on difficulty, price, and cuisine.

        Args:
            combatant (Meal): The combatant we want the battle score of.

        Returns:
            The battle score of inputted combatant.
=======
        Calculates the battle score based on price, cuisine, and difficulty.

        Args:
            combatant (Meal): The Meal instance representing the combatant.

        Returns:
            float: The calculated battle score.
>>>>>>> f7dfcc7d2e0018a70890860b121e5b175fecb00d
        """
        difficulty_modifier = {"HIGH": 1, "MED": 2, "LOW": 3}

        # Log the calculation process
        logger.info("Calculating battle score for %s: price=%.3f, cuisine=%s, difficulty=%s",
                    combatant.meal, combatant.price, combatant.cuisine, combatant.difficulty)

        # Calculate score
        score = (combatant.price * len(combatant.cuisine)) - difficulty_modifier[combatant.difficulty]

        # Log the calculated score
        logger.info("Battle score for %s: %.3f", combatant.meal, score)

        return score

    def get_combatants(self) -> List[Meal]:
        """
<<<<<<< HEAD
        Returns the info of combatants in the battle.

        Returns:
            List of combatants in battle.
=======
        Returns the current list of combatants.

        Returns:
            List[Meal]: Current list of combatants.
>>>>>>> f7dfcc7d2e0018a70890860b121e5b175fecb00d
        """
        logger.info("Retrieving current list of combatants.")
        return self.combatants

    def prep_combatant(self, combatant_data: Meal):
        """
<<<<<<< HEAD
        Adds a combatant to the battle.
        
        Args: 
            combatant_data (Meal): combatant being added to the battle.

        Raises: 
            ValueError: If the current battle is already full.
=======
            Adds a new combatant to prepare them for battle if there is enough space.

            Args:
                combatant_data (Meal): The meal to add as a combatant.

            Raises:
                ValueError: If the combatants list already has two entries.
>>>>>>> f7dfcc7d2e0018a70890860b121e5b175fecb00d
        """
        if len(self.combatants) >= 2:
            logger.error("Attempted to add combatant '%s' but combatants list is full", combatant_data.meal)
            raise ValueError("Combatant list is full, cannot add more combatants.")

        # Log the addition of the combatant
        logger.info("Adding combatant '%s' to combatants list", combatant_data.meal)

        self.combatants.append(combatant_data)

        # Log the current state of combatants
        logger.info("Current combatants list: %s", [combatant.meal for combatant in self.combatants])
