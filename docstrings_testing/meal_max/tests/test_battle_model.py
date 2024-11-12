import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import *
from meal_max.utils import *

##################################################
# Fixtures
##################################################

@pytest.fixture
def battle_model(): 
    """fixture to provide a new BattleModel instance for each test"""
    return BattleModel()

@pytest.fixture
def meal1():
    """fixture to provide a meal instance for each test"""
    return Meal(id=1, meal="Pasta", cuisine="Italian", price=6.0, difficulty="LOW")

@pytest.fixture
def meal2():
    """fixture to provide a secondary meal instance for each test"""
    return Meal(id=2, meal="Wings", cuisine="American", price=9.0, difficulty="MED")

@pytest.fixture
def meal3():
    """fixture to provide a tertiary meal instance for each test"""
    return Meal(id=3, meal="Hamburger", cuisine="American", price=8.0, difficulty="LOW")

def mock_update_meal_stats(meal_id, status):
    pass

##################################################
# Battle Function Test Case
##################################################

def test_valid_battle(battle_model, meal1, meal2, monkeypatch):
    """test conducting a battle"""
    monkeypatch.setattr('meal_max.models.battle_model.update_meal_stats', mock_update_meal_stats)

    battle_model.prep_combatant(meal1)
    battle_model.prep_combatant(meal2)

    winner = battle_model.battle()

    assert winner in [meal1.meal, meal2.meal]

    assert len(battle_model.get_combatants()) == 1

def test_emptied_battle(battle_model, meal1):
    """test conducting an invalid battle"""
    battle_model.prep_combatant(meal1)

    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()

##################################################
# Management Function Test Cases
##################################################

def test_clear_battle(battle_model, meal1, meal2):
    """test conducting a clearing of battle"""
    battle_model.prep_combatant(meal1)
    battle_model.prep_combatant(meal2)

    assert len(battle_model.get_combatants()) == 2

    battle_model.clear_combatants()

    assert len(battle_model.get_combatants()) == 0

def test_battle_score(battle_model, meal1, meal2):
    """test ensuring valid battle scores"""
    score1 = battle_model.get_battle_score(meal1)
    score2 = battle_model.get_battle_score(meal2)

    assert score1 == 39.0
    assert score2 == 70.0

def test_get_combatants(battle_model, meal1, meal2):
    """test ensuring we can retrieve current combatants"""
    battle_model.prep_combatant(meal1)
    battle_model.prep_combatant(meal2)
    
    combatants_list = battle_model.get_combatants()

    assert meal1 in combatants_list
    assert meal2 in combatants_list

def test_prep_combatants(battle_model, meal1, meal2):
    """test ensuring we properly add meals to our combatants list"""
    battle_model.prep_combatant(meal1)
    battle_model.prep_combatant(meal2)

    combatants_list = battle_model.get_combatants()

    assert meal1 in combatants_list
    assert meal2 in combatants_list

def test_prep_to_full_battle(battle_model, meal1, meal2, meal3):
    """test battle does not allow > 2 combatants"""
    battle_model.prep_combatant(meal1)
    battle_model.prep_combatant(meal2)

    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(meal3)