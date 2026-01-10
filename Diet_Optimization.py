# HW 11 11/04/2025 ACF

import pulp #import PuLP library for linear programming
import pandas as pd #import pandas for data handling
import string


#Load diet data from Excel (contains foods plus min/max daily requirements)
diet_data = pd.read_excel('diet.xls')


#Keep only the rows that list actual foods (drop the separator rows)
food_table = diet_data[diet_data['Foods'].notna()].copy()
#take the slice of the dataset that corresponds to food data
#Make a copy to avoid working with a view
food_table.set_index('Foods', inplace=True)
#now we indexing by food name instead of row number


#Get the minimum and maximum nutrition constraints from the bottom rows
requirements_table = diet_data.tail(2).reset_index(drop=True)
#use tail to get last two rows (min and max constraints)
#reset index from 0 so we don't have to keep track of original row numbers
min_row = requirements_table.iloc[0] #iloc gets row by position
max_row = requirements_table.iloc[1]

nutrients = ['Calories', 'Cholesterol mg', 'Total_Fat g', 'Sodium mg',
    'Carbohydrates g', 'Dietary_Fiber g', 'Protein g', 'Vit_A IU', 'Vit_C IU',
    'Calcium mg', 'Iron mg']

#Extract min and max requirements into dictionaries
min_requirements = {}
for nutrient in nutrients:
    min_requirements[nutrient] = float(min_row[nutrient])

max_requirements = {}
for nutrient in nutrients:
    max_requirements[nutrient] = float(max_row[nutrient])


#Build the nutrition dictionaries
prices = {}
for food, price in food_table['Price/ Serving'].items():
    prices[food] = price

#dictionary of dictionaries
#nutrient_content[nutrient][food]; outer dict keys nutrients, inner dict keys foods
nutrient_content = {}
for nutrient in nutrients:
    nutrient_content[nutrient] = {}
    for food, value in food_table[nutrient].astype(float).items():
        nutrient_content[nutrient][food] = value


def safe_name(raw):
    #replace characters PuLP dislikes (spaces, punctuation) with underscores
    allowed = string.ascii_letters + string.digits + '_'
    return ''.join(ch if ch in allowed else '_' for ch in raw)


#Define linear program model
#LpProblem(name, sense), PuLP's constuctor for model
#Name is the label for the model
# LpMinimize (and LpMaximize) are the two senses, they direct the objective
diet_model = pulp.LpProblem('Cheapest_Diet', pulp.LpMinimize)

#Define decision variables
#1. we can decide whether to select a food
#2. we can decide how much to select
#LpVariable.dicts(name, keys, lowBound, upBound, cat)
#name = base name for the variables
#keys = list of keys to create variables for (here, food names, which we get from our
# food_table, which has food names as its index)
#lowBound = minimum value for the variable (default is None, no lower bound)
#upBound = maximum value for the variable (default is None, no upper bound)
#Cat = 'Continuous'/'Integer'/'Binary' (default is 'Continuous')

servings = pulp.LpVariable.dicts('servings', food_table.index, lowBound=0)
#lowBound 0, can't have negative servings
selected = pulp.LpVariable.dicts('selected', food_table.index, cat='Binary') 
#cat binary, yes or no whether selected


#Objective: minimize total cost of the diet
#Objective function is added to the model by adding a "Total Cost" term to the model
diet_model += pulp.lpSum(prices[food] * servings[food] for food in food_table.index), 'TotalCost'
#lpSum is a PuLP function that sums up a list of terms
#we do sume of price * servings for each food in the food table


#If a food is selected, then a minimum of 1/10 serving must be chosen.
MIN_SELECTED_SERVING = 0.1 

#write a constraint to link serving and selected variables (only get servings if selected is 1)
for food in food_table.index:
    #since we cannot use if-then in LP, we use (the lower-bound half)
    #of a big-M style constraint
    serving_floor = MIN_SELECTED_SERVING * selected[food]
    #serving_floor is 0.1 if selected is 1, otherwise 0
    diet_model += servings[food] >= serving_floor, f"{safe_name(food)}_min_selection"
    #if selected == 1, enforce >=0.1; if selected == 0, servings can stay at 0

#Nutrition constraints: enforce minimums and maximums for every nutrient
for nutrient in nutrients:
    #enforce the minimum required amount for this nutrient
    safe_nutrient = safe_name(nutrient)
    diet_model += (
        pulp.lpSum(nutrient_content[nutrient][food] * servings[food] for food in food_table.index)
        >= min_requirements[nutrient]
    ), f'{safe_nutrient}_minimum'

    #enforce the maximum allowed amount for this nutrient
    diet_model += (
        pulp.lpSum(nutrient_content[nutrient][food] * servings[food] for food in food_table.index)
        <= max_requirements[nutrient]
    ), f'{safe_nutrient}_maximum'


#Many people dislike celery and frozen broccoli.
#So at most one, but not both, can be selected.
diet_model += selected['Celery, Raw'] + selected['Frozen Broccoli'] <= 1, 'Celery_or_Broccoli'


#To get day-to-day variety in protein, at least 3 kinds of meat/poultry/fish/eggs must be selected
# list of foods we are counting as protein sources for the variety requirement
protein_foods = [
    'Roasted Chicken', 'Poached Eggs', 'Scrambled Eggs', 'Bologna,Turkey',
    'Frankfurter, Beef', 'Ham,Sliced,Extralean', 'Kielbasa,Prk', 'Hamburger W/Toppings',
    'Hotdog, Plain', 'Pork', 'Sardines in Oil', 'White Tuna in Water',
    'Pizza W/Pepperoni', 'Taco', 'Beanbacn Soup,W/Watr', 'Splt Pea&Hamsoup',
    'Chicknoodl Soup', 'Neweng Clamchwd', 'New E Clamchwd,W/Mlk'
]

#sum of selected protein foods must be at least 3
diet_model += pulp.lpSum(selected[food] for food in protein_foods) >= 3, 'Protein_Variety'


#Solve the linear program (use HiGHS solver)
diet_model.solve(pulp.HiGHS(msg=False))


#Report solution status and total cost
status = pulp.LpStatus[diet_model.status]
#LpStatus converts solver status code into a readable string
#diet_model.status stores the raw solver code; key values include Optimal, Infeasible, Unbounded, Not Solved
print('Solver status:', status)

total_cost = pulp.value(diet_model.objective)
#pulp.value extracts the numeric value of the objective expression
#using two decimal places for currency formatting
print('Minimum daily cost: ${:.2f}'.format(total_cost))


#List foods that appear in the optimal diet along with serving counts and cost contribution
solution_rows = []
for food in food_table.index:
    quantity = servings[food].varValue
    #varValue accesses the optimized value of the variable
    if quantity > 0:
        cost = prices[food] * quantity
        solution_rows.append((food, quantity, cost))

for food, quantity, cost in sorted(solution_rows, key=lambda x: -x[1]):
    #sorted so that foods with the largest servings appear first
    print(f'{food}: {quantity:.2f} servings, cost ${cost:.2f}')


#Calculate achieved nutrient levels to confirm feasibility
for nutrient in nutrients:
    achieved = sum(nutrient_content[nutrient][food] * servings[food].varValue for food in food_table.index)
    #print actual intake for each nutrient alongside the min/max limits
    print(f'{nutrient}: {achieved:.2f} (min {min_requirements[nutrient]}, max {max_requirements[nutrient]})')
