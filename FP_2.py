"""FINAL PROJECT - HUDS Nutrition Scorer - Marta Amani"""

import requests
import csv
import textwrap
import re
import string
import os
import webbrowser
import tempfile
from dotenv import load_dotenv

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.align import Align
console = Console()
console = Console(record=True)


# Global variables
stop_word_list = ["a", "an", "the", "and", "or", "of","with", "in", "on", "for", "to", "at"]
punctuation = string.punctuation.replace('*', '')

# Part 1: API conection

load_dotenv()
def connection(recipe_name):
    """Fetch recipe data from HUDS API and """

    console.print('Searching recipe from the Harvard University Dining Service\n')

    url = "https://go.apis.huit.harvard.edu/ats/dining/v3/recipes"
    params = {"name": recipe_name}
    headers = {
        "User-Agent": "FP Project Cs 32",
        "X-Api-Key":  os.getenv("API_KEY")
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200:
        console.print("Error: bad response from server")
        return None
    if not response.text.strip():
        console.print("Error: empty response")
        return None

    data = response.json()

    if len(data) == 0:
        console.print(f"No recipes found for '{recipe_name}'")
        return None

    return data

# Part 2:  Recipe Search and match

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
        console.print(f'No exact match found for "{recipe_name}".')
        return None

    if len(partial) == 1:
        console.print(f'No exact match found for "{recipe_name}". The closest result is {partial[0].get("Recipe_Name")}')
        return partial[0]

    if len(partial) > 1:
        console.print(f'No exact match found for "{recipe_name}". Here are similar recipes: ')

    for i, suggestion in enumerate(partial):
        console.print(f"{i+1}. {suggestion.get("Recipe_Name")}")
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
    """Collect dietary filters from the user."""
    dietrary_preference = input("\nDo you have any dietary preferences? Type 'y' for yes, anything else for no.\n")
    if dietrary_preference.lower() == "y":
        console.print("\nDietary filters (optional). Type 'y' for yes, anything else for no.")
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
    else:
        return None

# Part 4: CSV Loader

def load_data():
    """ Load data from CSV file """
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
    """Score recipe based on ultra-processed additives found."""
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

    return {"score": recipe_score, "additives_found": additives_found,}

# Step 6: Nutrition socre/info + Pill display

# Step 7: Create a hisotry of the recipes and compare them
class Recipe:
    """Stores one searched recipe for session history."""

    def __init__(self, data, final_score):
        self.name = data.get("Recipe_Name")
        self.nova_score = final_score["score"]
        self.additives = final_score["additives_found"]

    def __str__(self):
        return f"{self.name:<45}  SCORE: {self.nova_score} / 100"

# Step 8: Logisitc regression?

# Step 9: Report Card
def clean_trailing(text):
    """Remove trailing whitespace, commas, and parentheses."""
    return re.sub(r'[\s,)(]+$', '', text)

def print_report(recipe, final_score):
    """
    Print a report card using rich.
    Called from main() after every successful search.
    """
    recipe_name = recipe.get("Recipe_Name", "")
    calories = recipe.get("Calories",   "N/A")
    allergens = clean_trailing(recipe.get("Allergens", "") or "")
    nutrition_score = final_score["score"]
    additives_found = final_score["additives_found"]

    # choose color based on score
    if nutrition_score >= 75:
        score_color = "green"
        score_icon  = "\N{Large Green Circle}"
    elif nutrition_score >= 50:
        score_color = "yellow"
        score_icon  = "\N{Large Yellow Circle}"
    else:
        score_color = "red"
        score_icon  = "\N{Large Red Circle}"

    # Header
    console.print()
    console.print(Panel(
        f"[bold cyan]{recipe_name}[/bold cyan]",
        title        = "[bold white]🍽 HUDS NUTRITION REPORT CARD[/bold white]",
        border_style = "cyan",
        padding      = (1, 4),
    ))

    # Score Bar
    filled = int((nutrition_score / 100) * 30)
    bar = "█" * filled + "░" * (30 - filled)

    console.print(
        f"\n  {score_icon}  [bold]Nutririon Score[/bold]   "
        f"[{score_color}][{bar}][/{score_color}]   "
        f"[bold {score_color}]{final_score} / 100[/bold {score_color}]"
    )

    # Nutrition info
    console.print("[bold]📊 Nutririon (% Daily Value) [/bold]")
    # add nutrion values
    console.print(f"\n[bold]Calories :[/bold]  {calories} kcal")
    console.print(f"[bold]Allergens:[/bold]  "
                  f"{'None listed' if not allergens else allergens}")

    # Dietary warnings
    #if warnings:
        #console.print()
        #for w in warnings:
            #console.print(f"  [bold yellow]{w}[/bold yellow]")

    # Additives table
    console.print()

    if additives_found:
        table = Table(
            title        = "⛔ Ultra-Processed Additives Found",
            box          = box.ROUNDED,
            border_style = "red",
            header_style = "bold red",
            show_lines   = True,
        )
        table.add_column("Additive",style="white", min_width=28)
        table.add_column("Category", style="yellow",min_width=18)
        table.add_column("Description", style="dim", min_width=25)

        for item in additives_found:
            table.add_row(
                item["name"],
                item["category"],
                item["description"],
            )

        console.print(table)

    else:
        console.print(Panel(
            "✅ [bold green]No ultra-processed additives found![/bold green]",
            border_style = "green",
        ))

    console.print()

    open_in_browser(console, recipe_name)

def open_in_browser(console, recipe_name):
    """
    Export the recorded rich console output to HTML
    and open it automatically in the default browser.

    Uses:
        console.export_html()  ← built into rich
        webbrowser.open()      ← built into Python
        tempfile               ← built into Python
    """
    # generate the HTML string from everything printed so far
    html = console.export_html(
        theme   = "solarized-dark",  # built-in rich theme
        inline_styles = True,        # self-contained file, no external CSS
    )

    # write to a temporary HTML file
    # tempfile creates a safe unique filename automatically
    tmp = tempfile.NamedTemporaryFile(
        mode    = "w",
        suffix  = ".html",
        delete  = False,
        encoding= "utf-8",
    )
    tmp.write(html)
    tmp.close()

    # open the file in the default browser
    webbrowser.open(f"file://{tmp.name}")
    print(f"\n  🌐  Report opened in browser → {tmp.name}")

# Step 0: Main Loop

def main():
    # Welcome message
    console.print(Panel(Align.center("[bold plum2]HUDS Nutrition Scorer[/bold plum2]\n"
        "[dim]Marta Amani  ·  Final Project CS32[/dim]"),
        border_style = "plum2",
        padding= (1, 4),
        width = 45,
    ))

    # Step 4
    additives_db = load_data()
    preferences = dietary_preference()
    history = [] # store the history of searched recipes in this session

    #prefereces = dietary_preference()

    while True:
        search = input("Which recipe would you like to search? (or 'q' to quit): ").strip() # we strip so that we can still look for a math
                                                                                            # if the user added a space at the beginnig by accident
        if search.lower() == "q":
            console.print("Goodbye!")
            break

        data = connection(search)

        if not data:
            console.print(f"Could not connect to the HUDS server. Please try again.[/red]")
            continue # API failed

        recipe = find_recipe(search, data)

        if not recipe:
            console.print(f'No recipe found for "{search}". Please try another search term.[/red]')
            continue # no recipe found

        # Main output
        max_len = len("Ingredients:")
        console.print(f"{'Recipe:':<{max_len}} {recipe.get('Recipe_Name')}")
        ingredients_list = recipe.get('Ingredient_List') or "N/A"
        console.print(textwrap.fill(ingredients_list.strip(" \t\n,)( "), width=80, initial_indent="Ingredients: ",subsequent_indent=" " * 13))
        console.print(f"{'Calories:':<{max_len}} {recipe.get('Calories')}")
        allergens_list = recipe.get('Allergens') or "N/A"
        console.print(f"{'Allergens:':<{max_len}} {allergens_list.strip(" \t\n,)( ")}")

        final_score = create_score(recipe, additives_db)
        console.print(f"Score: {final_score['score']} / 100")

        # Dietary warnings
        # ingredients = (recipe.get("Ingredient_List") or "").lower()
        #warnings = []

        num_additives = len(final_score["additives_found"])
        if final_score["additives_found"]:
            console.print(f"\nAdditive(s) found in this recipe = {num_additives}. Here are the details:")
            for item in final_score["additives_found"]:
                console.print(f"  - {item['name']}: {item['description']}")
        else:
            console.print("No ultra-processed additives found!")

        print_report(recipe, final_score)

        console.print("\nType another recipe name to keep searching, or 'q' to quit.")


if __name__ == "__main__":
    main()
