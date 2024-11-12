#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5002/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service 
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

##########################################################
#
# Meal Management
#
##########################################################

create_meal(){
    meal=$1
    cuisine=$2
    price=$3
    difficulty=$4

    echo "Adding meal ($meal) to the meals table..."
    curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
        -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}" | grep -q '"status": "success"'

    if [ $? -eq 0 ]; then
        echo "Meal added successfully."
    else
        echo "Failed to add meal."
        exit 1
    fi
}

clear_catalog() {
  echo "Clearing catalog..."
  response=$(curl -s -X DELETE "$BASE_URL/clear-meals")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Catalog cleared successfully."
  else
    echo "Failed to clear catalog."
    exit 1
  fi
}


delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_name() {
  meal_name=$1

  echo "Getting meal by name ($meal_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name ($meal_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (name: $meal_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by name ($meal_name)."
    exit 1
  fi
}

############################################################
#
# Conduct Battle
#
############################################################

begin_battle() {
  echo "Starting the current battle..."
  response=$(curl -s -X GET "$BASE_URL/battle")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle successfully conducted."
  else
    echo "Failed to start current battle."
    exit 1
  fi
}

clear_battle(){
    echo "Clearing current battle..."
    response=$(curl -s -X DELETE "$BASE_URL/clear-meals")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Meals cleared successfully."
    else
        echo "Failed to clear meals."
        exit 1
    fi
}

get_all_meals_from_battle() {
  echo "Retrieving all meals from current battle..."
  response=$(curl -s -X GET "$BASE_URL/get-combatants")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "All meals retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meals JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve all meals from playlist."
    exit 1
  fi
}

add_meal_to_battle() {
  meal=$meal_name

  echo "Adding meal to battle: ($meal_name)..."
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" \
    -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal added to battle successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add meal to battle."
    exit 1
  fi
}

get_leaderboard() {
  echo "Retrieving leaderboard..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."
  else
    echo "Failed to retrieve leaderboard."
    exit 1
  fi
}


check_health
check_db

create_meal "Pasta" "Italian" 7.0 "LOW"
create_meal "Ramen" "Japanese" 5.0 "MED"
create_meal "Soup" "British" 3.0 "LOW"
create_meal "Jerky" "American" 6.0 "HIGH"

get_meal_by_name "Jerky"

delete_meal_by_id 3
get_leaderboard
get_meal_by_id 1
get_meal_by_name "Pasta"

add_meal_to_battle "Pasta"
add_meal_to_battle "Ramen"

get_all_meals_from_battle

begin_battle
get_leaderboard

clear_catalog