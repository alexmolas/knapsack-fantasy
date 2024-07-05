# Biwenger Knapsack Solver

This project implements a fantasy football team optimizer for Biwenger, using a knapsack algorithm to select the best possible team within given constraints.

## Overview

The Biwenger Knapsack Solver is designed to help users create optimal fantasy football teams by maximizing player value while adhering to specific team constraints. It uses the Google OR-Tools library to solve the knapsack problem and select the best combination of players.

## Features
- Fetches player data from the Biwenger API
- Implements team constraints (e.g., maximum salary, player positions)
- Optimizes team selection based on player value and cost
- Supports captain selection for additional team value


## Installation
1. Clone the repository
2. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage
To run the optimizer:

```
python best_team.py
```

This script will fetch player data, solve the optimization problem, and output the best team 
configuration.

## Project Structure
- `biwenger_knapsack/`: Main package containing the core functionality
  - `api.py`: Handles API requests to fetch player data
  - `models.py`: Defines data models for players and teams
  - `parser.py`: Parses raw player data into structured objects
  - `solver.py`: Implements the knapsack algorithm for team optimization
  - `utils.py`: Utility functions for displaying team information
- `best_team.py`: Main script to run the optimization
