"""FINAL PROJECT - HUDS Nutrition Scorer - Marta Amani"""

import requests

def get_ingredients(recipe_name):
    print('Searching ingredients from the Harvard Univeristy Dining Service Website\n')

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


def dietary_preference()


def main():
    while True:
        search = input("Which recipe would you like to search? (or 'q' to quit): ")

        if search.lower() == "q":
            print("Goodbye!")
            break

        recipe = get_ingredients(search)

        if recipe:
            print(f"Recipe:      {recipe.get('Recipe_Name')}")
            print(f"Ingredients: {recipe.get('Ingredient_List')}")
            print(f"Calories:    {recipe.get('Calories')}")
            print(f"Allergens:   {recipe.get('Allergens')}")
            break

if __name__ == "__main__":
    main()
