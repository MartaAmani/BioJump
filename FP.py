"""FINAL PROJECT - HUDS Nutrition Scorer - Marta Amani"""

import requests
import csv
import textwrap
import re
import string
install pip
pip install python-dotenv


# Part 1 and Part 2:  API and Recipe Search

stop_word_list = ["a", "an", "the", "and", "or", "of","with", "in", "on", "for", "to", "at"]
punctuation = string.punctuation.replace('*', '')

def get_wordlist(text, remove_stopwords=True):
    """Convert text into a list of clean lowercase words."""

    text = text.lower()

    # Extract words from text
    pattern = '^[{0}]+|[{0}]+$'.format(punctuation) # remove punctuation only from the beginning or end
    words = [re.sub(pattern, '', w) for w in text.split()] # re.sub(pattern, '', w) removes punctuation from the start
                                                        # and end of each word coming from .split()

    # By default, remove stopwords from wordlist
    if remove_stopwords:
        return [w for w in words if w not in stop_word_list]
    else:
        return words


def partial_match(search, recipe_name):
    """Return True if the search appears in any recipe name"""
    search_words = get_wordlist(search)
    recipe_words = get_wordlist(recipe_name)
    return any(word in recipe_words for word in search_words) # True if at least one search word is found in the recipe word list


def connection(recipe_name):
    """Fetch recipe data from HUDS API and """

    print('Searching recipe from the Harvard University Dining Service\n')

    url = "https://go.apis.huit.harvard.edu/ats/dining/v3/recipes"
    params = {"name": recipe_name}
    headers = {
        "User-Agent": "FP Project Cs 32",
        "X-Api-Key":  Apy_key
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200:
        print("Error: bad response from server")
        return None
    if not response.text.strip():
        print("Error: empty response")
        return None

    data = response.json()

    if len(data) == 0:
        print(f"No recipes found for '{recipe_name}'")
        return None

    return data

def find_recipe(recipe_name, data):
    ''' Search a list of recipe dicts for the best match to 'search'.'''
    search = recipe_name.upper() # all the names are uppercase

    # Exact match between the input name and one name in the list
    exact = []
    for recipe in data:
        name = recipe.get("Recipe_Name", "")
        ingredients = recipe.get("Ingredient_List", "")
        if name.upper() == search and ingredients.strip():
            exact.append(recipe)
    if exact:
        return exact[0]

    # Word overlap match between the input name and one name in the list
    partial = []
    seen = set() # to avoid duplicates in the partial match list
    for recipe in data:
        name = recipe.get("Recipe_Name", "")
        ingredients = recipe.get("Ingredient_List", "")
        if partial_match(recipe_name, name) and ingredients.strip():
            if name not in seen:
                seen.add(name)
                partial.append(recipe)

    if len(partial) == 0:
        print(f'No exact match found for "{recipe_name}".')
        return None

    if len(partial) == 1:
        print(f'No exact match found for "{recipe_name}". The closest result is {partial[0].get("Recipe_Name")}')
        return partial[0]

    if len(partial) > 1:
        print(f'No exact match found for "{recipe_name}". Here are similar recipes: ')

    for i, suggestion in enumerate(partial):
        print(f"{i+1}. {suggestion.get("Recipe_Name")}")
    while True:
        choice = input("\nEnter a number to select a recipe (or 0 to cancel): ").strip()
        if choice == "0":
            return None
        if choice.isdigit():
            index = int(choice) - 1
            if index in range(len(partial)):
                return partial[index]
        return None

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

    return additives_db

# Step 5: Processed food score
def create_score(recipe, additives_db):
    # grab the list of the ingredients
    raw_ingredients = recipe.get("Ingredient_List", "") or ""
    raw_ingredients = raw_ingredients.lower()
    # compare each ingredeint with the additives disctonary to see if any of the ingredient is present

    # for each mathced additive reduce the score by 5 points (max score is 100)
    # create a list of the additive present in the recipe and store them (we'll print them later)
    recipe_score = 100
    additives_found = []

    for additive, info in additives_db.items():
        if additive in raw_ingredients:
            recipe_score = recipe_score - 5
            additives_found.append({
                "name":       additive,
                "category":   info["category"],
                "description": info["description"],
            })

    recipe_score = max(0, recipe_score) # the score cannot go below 0

    return {
        "score":           recipe_score,
        "additives_found": additives_found,
    }

# Step 6: Nutrition socre/info + Pill display

# Step 7: Create a hisotry of the recipes and compare them

# Step 8: Dietary flag checker

# Step 9: Logisitc regression?

# Step 10: Report Card

# Step 0: Main Loop

def main():

    # Step 4
    additives_db = load_data()

    #prefereces = dietary_preference()

    while True:
        search = input("Which recipe would you like to search? (or 'q' to quit): ").strip() # we strip so that we can still look for a math
                                                                                            # if the user added a space at the beginnig by accident
        if search.lower() == "q":
            print("Goodbye!")
            break

        data = connection(search)

        if not data:
            continue # API failed

        recipe = find_recipe(search, data)

        if not recipe:
            continue # no recipe found

        max_len = len("Ingredients:")
        print(f"{'Recipe:':<{max_len}} {recipe.get('Recipe_Name')}")
        ingredients_list = recipe.get('Ingredient_List') or "N/A"
        print(textwrap.fill(ingredients_list.strip(" \t\n,)( "), width=80, initial_indent="Ingredients: ",subsequent_indent=" " * 13))
        print(f"{'Calories:':<{max_len}} {recipe.get('Calories')}")
        allergens_list = recipe.get('Allergens') or "N/A"
        print(f"{'Allergens:':<{max_len}} {allergens_list.strip(" \t\n,)( ")}")

        final_score = create_score(recipe, additives_db)
        print(f"Score: {final_score['score']} / 100")

        num_additives = len(final_score["additives_found"])
        if final_score["additives_found"]:
            print(f"\nAdditive(s) found in this recipe = {num_additives}. Here are the details:")
            for item in final_score["additives_found"]:
                print(f"  - {item['name']}: {item['description']}")
        else:
            print("No ultra-processed additives found!")

        print("\nType another recipe name to keep searching, or 'q' to quit.")


if __name__ == "__main__":
    main()
