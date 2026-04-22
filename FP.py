"""FINAL PROJECT - HUDS Nutrition Scorer - Marta Amani"""

import requests
import csv
import textwrap


# Part 1 and Part 2:  API and Recipe Search

def get_ingredients(recipe_name):
    print('Searching recipe from the Harvard Univeristy Dining Service Website\n')

    # craft a request
    url = f"https://go.apis.huit.harvard.edu/ats/dining/v3/recipes"

    params = {"name": recipe_name}
    headers = {
        "User-Agent": "FP Project Cs 32",
        "X-Api-Key": "reC5wGF3ZYFyQQodPHKXwelidEpVnir8EJUD6DDadGnT6J7S"
    }

    response = requests.get(url, params=params, headers=headers)

    # DEBUG
    # print(f"Status code: {response.status_code}")
    # print(f"URL called: {response.url}")
    # print(f"Raw response: {response.text[:500]}")

    if response.status_code != 200:
        print("Error: bad response from server")
        return None

    if not response.text.strip():
        print("Error: empty response")
        return None

    data = response.json() # parse a JSON-formatted API response into a native Python data structure

    if len(data) == 0:
        print(f"No recipes found for '{recipe_name}'")
        return None

    search = recipe_name.upper() # all the names are uppercase

    # Match the input name with one name in the list
    matching = []
    for recipe in data:
        name = recipe.get("Recipe_Name", "")
        ingredients = recipe.get("Ingredient_List", "")
        if name.upper() == search and ingredients.strip():
            matching.append(recipe)

    if not matching:
        print(f'No exact match found for "{recipe_name}".')
        # Suggest recipe that is close
        close = []
        seen = set()
        for recipe in data:
            name = recipe.get("Recipe_Name")
            words = name.upper().split()
            if words[0] == search and name not in seen:
                close.append(name)
                seen.add(name)
        if close:
            print("Did you mean one of these?")
            for name in close:
                print(f"  - {name}")

        return None

    return matching[0] # return only one to delete duplicates


# Part 3: Dietary Preference Collector

def dietary_preference():
    print("\nDietary filters (optional). Type 'y' for yes, anything else for no.")
    preferences = {
        "vegan": {
            "enabled": input("Vegan? (y/n): ").lower() == "y",
            "forbidden": ["meat", "chicken", "fish", "egg", "milk", "cheese", "butter", "yogurt", "honey"],
        },
        "vegetarian": {
            "enabled": input("Vegetarian? (y/n): ").lower() == "y",
            "forbidden": ["meat", "chicken", "fish", "gelatin"],
        },
        "gluten_free": {
            "enabled": input("Gluten-free? (y/n): ").lower() == "y",
            "forbidden": ["wheat", "barley", "rye", "malt"],
        },
        "nut_free": {
            "enabled": input("Nut-free? (y/n): ").lower() == "y",
            "forbidden": ["almond", "walnut", "pecan", "cashew", "hazelnut", "peanut"],
        },
    }

    return preferences


# Part 4: CSV Loader

def load_data():
    """
    Load data from CSV file
    """

    additives_db = {}

    # Load additives
    with open('additives.csv', mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["additive"].strip().lower()
            additives_db[name] = {
            "category":   row["category"].strip(),
            "description": row["description"].strip(),
            }

    # Load carbon foot print

    return additives_db

# Step 5: Processed food score
def score():
    

# Step 6: Nutrition socre/info + Pill display

# Step 7: Carbon footprint score

# Step 8: Dietary flag checker

# Step 9: Logisitc regression?

# Step 10: Report Card

# Step 0: Main Loop

def main():
    while True:
        search = input("Which recipe would you like to search? (or 'q' to quit): ").strip() # we strip so that we can still look for a math
                                                                                            # if the user added a space at the beginnig by accident

        if search.lower() == "q":
            print("Goodbye!")
            break

        recipe = get_ingredients(search)
        max_len = len("Ingredients:")
        if recipe:
            print(f"{'Recipe:':<{max_len}} {recipe.get('Recipe_Name')}")
            print(textwrap.fill(recipe.get('Ingredient_List').rstrip(',)'), width=80, initial_indent="Ingredients: ",subsequent_indent=" " * 13))
            print(f"{'Calories:':<{max_len}} {recipe.get('Calories')}")
            print(f"{'Allergens:':<{max_len}} {recipe.get('Allergens').rstrip(', ')}")
            break

if __name__ == "__main__":
    main()
