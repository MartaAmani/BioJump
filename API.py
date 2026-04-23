def connection(recipe_name):
    """Fetch recipe data from HUDS API and """

    print('Searching recipe from the Harvard University Dining Service\n')

    url = "https://go.apis.huit.harvard.edu/ats/dining/v3/recipes"
    params = {"name": recipe_name}
    headers = {
        "User-Agent": "FP Project Cs 32",
        "X-Api-Key":  "reC5wGF3ZYFyQQodPHKXwelidEpVnir8EJUD6DDadGnT6J7S"
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
