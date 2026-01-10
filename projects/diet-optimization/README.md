# Diet Optimization (Linear Programming)
A mixed-integer optimization model that selects foods and serving sizes to minimize daily cost while meeting nutrition bounds.

## Problem
Given a food list with nutrient content and minimum/maximum daily requirements, choose servings to minimize total cost. Add business rules to enforce variety and avoid undesirable combinations.

## Solution
The script builds a linear program in PuLP with:
- Continuous decision variables for servings.
- Binary variables indicating whether a food is selected.
- Objective: minimize total cost.
- Constraints for nutrient minimums and maximums, selection logic, and variety.

It reads `diet.xls`, solves with the HiGHS solver, and prints the optimal foods, cost, and achieved nutrient totals.

## Highlights
- Mixed-integer linear optimization (binary + continuous decision variables).
- Nutrition constraints with lower and upper bounds.
- Extra rules for mutual exclusion and protein variety.

## How to run
```bash
python3 HW11-2.py
```

Input file: `diet.xls` must be in the same folder as the script.

## Adjust these parameters
- `MIN_SELECTED_SERVING` to change the minimum serving size when a food is selected.
- `protein_foods` list to change the variety requirement.
