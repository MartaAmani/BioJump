import requests

def get_all_recipes():
    url = "https://go.apis.huit.harvard.edu/ats/dining/v3/recipes"
    headers = {
        "User-Agent": "FP Project Cs 32",
        "X-Api-Key": "reC5wGF3ZYFyQQodPHKXwelidEpVnir8EJUD6DDadGnT6J7S"  # Client ID 
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Error:", response.status_code)
        return

    data = response.json()

    print(f"Total recipes found: {len(data)}\n")

    recipe_index = {}
    for r in data:
        name = r.get("Recipe_Name", "").strip()
        recipe_id = r.get("Recipe_Number", "").strip()
        if name and recipe_id:
            recipe_index[name] = recipe_id # Assignining the recipe ID to "name" in the dictonary

    for name in sorted(recipe_index.keys()):
        print(f"{name}: {recipe_index[name]}")

get_all_recipes()


