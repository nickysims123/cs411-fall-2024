from contextlib import contextmanager
import re
import sqlite3
import pytest

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
)

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for SELECT queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor for individual test configurations 

def test_create_meal(mock_cursor):
    """Test creating a new meal"""
    create_meal(meal="Ramen", cuisine="Japanese", price=12.5, difficulty="MED")

    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]

    expected_arguments = ("Ramen", "Japanese", 12.5, "MED")
    assert actual_arguments == expected_arguments, (f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}.")

def test_create_meal_duplicate(mock_cursor):
    """Test creating a meal with a duplicate name (should raise an error)."""
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meals.meal")

    with pytest.raises(ValueError, match="Meal with name 'Ramen' already exists"):
        create_meal(meal="Ramen", cuisine="Japanese", price=12.5, difficulty="MED")

def test_create_meal_invalid_price():
    """Test error when trying to create a meal with an invalid price (e.g., negative or non-numeric)."""
    with pytest.raises(ValueError, match="Invalid price: -10.0. Price must be a positive number."):
        create_meal(meal="Ramen", cuisine="Japanese", price=-10.0, difficulty="HIGH")

    with pytest.raises(ValueError, match="Invalid price: xyz. Price must be a positive number."):
        create_meal(meal="Ramen", cuisine="Japanese", price="xyz", difficulty="HIGH")

def test_create_meal_invalid_difficulty():
    """Test error when trying to create a meal with an invalid difficulty level."""
    with pytest.raises(ValueError, match="Invalid difficulty level: MASTER CHEF. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Ramen", cuisine="Japanese", price=15.0, difficulty="MASTER CHEF")

def test_delete_meal(mock_cursor):
    """Test soft deleting a meal from the catalog by meal ID."""
    mock_cursor.fetchone.return_value = ([False])

    delete_meal(1)

    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, (f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}.")
    assert actual_update_args == expected_update_args, (f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}.")

def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a meal that's already marked as deleted."""
    mock_cursor.fetchone.return_value = [True]

    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        delete_meal(999)
    
def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent meal."""
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_get_leaderboard_wins(mock_cursor):
    """Test retrieving the leaderboard sorted by wins."""
    mock_cursor.fetchall.return_value = [
        (5, "BBQ Ribs", "American", 20.0, "HIGH", 25, 20, 0.8),
        (2, "Beef Wellington", "French", 30.0, "HIGH", 20, 15, 0.75),
        (4, "Sushi Roll", "Japanese", 15.0, "MED", 18, 12, 0.70),
        (1, "Chicken Alfredo", "Italian", 12.5, "MED", 15, 10, 0.60),
        (3, "Pad Thai", "Thai", 10.0, "LOW", 12, 8, 0.55),
    ]

    leaderboard = get_leaderboard(sort_by="wins")

    expected_leaderboard = [
        {'id': 5, 'meal': "BBQ Ribs", 'cuisine': "American", 'price': 20.0, 'difficulty': "HIGH", 'battles': 25, 'wins': 20, 'win_pct': 80.0},
        {'id': 2, 'meal': "Beef Wellington", 'cuisine': "French", 'price': 30.0, 'difficulty': "HIGH", 'battles': 20, 'wins': 15, 'win_pct': 75.0},
        {'id': 4, 'meal': "Sushi Roll", 'cuisine': "Japanese", 'price': 15.0, 'difficulty': "MED", 'battles': 18, 'wins': 12, 'win_pct': 70.0},
        {'id': 1, 'meal': "Chicken Alfredo", 'cuisine': "Italian", 'price': 12.5, 'difficulty': "MED", 'battles': 15, 'wins': 10, 'win_pct': 60.0},
        {'id': 3, 'meal': "Pad Thai", 'cuisine': "Thai", 'price': 10.0, 'difficulty': "LOW", 'battles': 12, 'wins': 8, 'win_pct': 55.0}
    ]

    assert leaderboard == expected_leaderboard, f"Expected {expected_leaderboard}, but got {leaderboard}"

    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
        ORDER BY wins DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_leaderboard_win_pct(mock_cursor):
    """Test retrieving the leaderboard sorted by win percentage with real meal examples."""
    mock_cursor.fetchall.return_value = [
        (5, "BBQ Ribs", "American", 20.0, "HIGH", 25, 20, 0.8),
        (2, "Beef Wellington", "French", 30.0, "HIGH", 20, 15, 0.75),
        (4, "Sushi Roll", "Japanese", 15.0, "MED", 18, 12, 0.70),
        (1, "Chicken Alfredo", "Italian", 12.5, "MED", 15, 10, 0.60),
        (3, "Pad Thai", "Thai", 10.0, "LOW", 12, 8, 0.55),
    ]

    leaderboard = get_leaderboard(sort_by="win_pct")

    expected_leaderboard = [
        {'id': 5, 'meal': "BBQ Ribs", 'cuisine': "American", 'price': 20.0, 'difficulty': "HIGH", 'battles': 25, 'wins': 20, 'win_pct': 80.0},
        {'id': 2, 'meal': "Beef Wellington", 'cuisine': "French", 'price': 30.0, 'difficulty': "HIGH", 'battles': 20, 'wins': 15, 'win_pct': 75.0},
        {'id': 4, 'meal': "Sushi Roll", 'cuisine': "Japanese", 'price': 15.0, 'difficulty': "MED", 'battles': 18, 'wins': 12, 'win_pct': 70.0},
        {'id': 1, 'meal': "Chicken Alfredo", 'cuisine': "Italian", 'price': 12.5, 'difficulty': "MED", 'battles': 15, 'wins': 10, 'win_pct': 60.0},
        {'id': 3, 'meal': "Pad Thai", 'cuisine': "Thai", 'price': 10.0, 'difficulty': "LOW", 'battles': 12, 'wins': 8, 'win_pct': 55.0}
    ]

    assert leaderboard == expected_leaderboard, f"Expected {expected_leaderboard}, but got {leaderboard}"

    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
        ORDER BY win_pct DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_leaderboard_invalid_sort(mock_cursor):
    """Test error when an invalid sort_by parameter is provided."""
    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid_sort"):
        get_leaderboard(sort_by="invalid_sort")

def test_get_meal_by_id(mock_cursor):
    """Test retrieving a meal by its ID."""

    mock_cursor.fetchone.return_value = (1, "Ramen", "Japanese", 12.5, "MED", False)

    result = get_meal_by_id(1)

    expected_result = Meal(id=1, meal="Ramen", cuisine="Japanese", price=12.5, difficulty="MED")

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]

    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, (f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}.")

def test_get_meal_by_id_deleted(mock_cursor):
    """Test error when retrieving a meal that has been deleted."""
    mock_cursor.fetchone.return_value = (1, "Ramen", "Japanese", 12.5, "MED", True)

    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        get_meal_by_id(1)

def test_get_meal_by_bad_id(mock_cursor):
    """Test error when retrieving a meal that does not exist."""
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

def test_get_meal_by_name(mock_cursor):
    """Test retrieving a meal by its name."""
    mock_cursor.fetchone.return_value = (2, "Curry", "Indian", 10.0, "HIGH", False)

    result = get_meal_by_name("Curry")

    expected_result = Meal(id=2, meal="Curry", cuisine="Indian", price=10.0, difficulty="HIGH")

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]

    expected_arguments = ("Curry",)
    assert actual_arguments == expected_arguments, (f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}.")

def test_get_meal_by_name_deleted(mock_cursor):
    """Test error when retrieving a meal that has been deleted by name."""
    mock_cursor.fetchone.return_value = (2, "Curry", "Indian", 10.0, "HIGH", True)

    with pytest.raises(ValueError, match="Meal with name Curry has been deleted"):
        get_meal_by_name("Curry")

def test_get_meal_by_bad_name(mock_cursor):
    """Test error when retrieving a meal that does not exist by name."""
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with name Rocks not found"):
        get_meal_by_name("Rocks")

def test_update_meal_stats_win(mock_cursor):
    """Test updating meal stats with a 'win' result."""
    mock_cursor.fetchone.return_value = [False]

    update_meal_stats(1, "win")

    expected_query = normalize_whitespace("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?")

    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_query == expected_query, "The SQL UPDATE query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, (f"The SQL UPDATE query arguments did not match. Expected {expected_arguments}, got {actual_arguments}.")

def test_update_meal_stats_loss(mock_cursor):
    """Test updating meal stats with a 'loss' result."""
    mock_cursor.fetchone.return_value = [False]

    update_meal_stats(2, "loss")

    expected_query = normalize_whitespace("UPDATE meals SET battles = battles + 1 WHERE id = ?")

    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_query == expected_query, "The SQL UPDATE query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    expected_arguments = (2,)
    assert actual_arguments == expected_arguments, (f"The SQL UPDATE query arguments did not match. Expected {expected_arguments}, got {actual_arguments}.")

def test_update_meal_stats_invalid_result(mock_cursor):
    """Test error when updating meal stats with an invalid result."""
    mock_cursor.fetchone.return_value = [False]

    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'."):
        update_meal_stats(3, "draw")

def test_update_meal_stats_deleted_meal(mock_cursor):
    """Test error when updating stats for a deleted meal."""
    mock_cursor.fetchone.return_value = [True]

    with pytest.raises(ValueError, match="Meal with ID 4 has been deleted"):
        update_meal_stats(4, "win")

def test_update_meal_stats_bad_id(mock_cursor):
    """Test error when updating stats for a non-existent meal."""
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        update_meal_stats(999, "loss")