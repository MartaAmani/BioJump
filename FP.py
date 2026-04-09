"""FINAL PROJECT - HUDS Nutrition Scorer - Marta Amani"""

import requests

def get_ingredients(recipe_name):
    print('Searching ingredients from the Harvard Univeristy Dining Service Website')

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

    search = recipe_name.upper() # all the names are uppercase
    matching = [r for r in data if r.get("Recipe_Name", "").lower() == search]

    if len(data) == 0:
        print(f"No recipes found for '{recipe_name}'")
        return None

    print(f"Found {len(data)} recipe(s) for '{recipe_name}':\n")

    for recipe in matching:
        print(f"Recipe:      {recipe.get('Recipe_Name')}\n")
        print(f"Ingredients: {recipe.get('Ingredient_List')}\n")
        print(f"Calories:    {recipe.get('Calories')}\n")
        print(f"Allergens:   {recipe.get('Allergens')}\n")
        print("-" * 40)

search = input('Which recipe would you like to search? ')
get_ingredients(search)
