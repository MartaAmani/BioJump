"""FINAL PROJECT - HUDS Nutrition Scorer - Marta Amani"""

import requests
import csv
import textwrap
import re
import string
import os
from dotenv import load_dotenv

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.align import Align
console = Console(record=True, highlight=False)


# Helpers
stop_word_list = ["a", "an", "the", "and", "or", "of","with", "in", "on", "for", "to", "at"]
punctuation = string.punctuation.replace('*', '')

def clean_trailing(text):
    """Remove trailing whitespace, commas, and parentheses."""
    return re.sub(r'[\s,)(]+$', '', text)

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

def score_color_icon(final_score):
    ''' choose color and icon based on the nutrition score'''
    if final_score >= 85:
        return "green", "\N{Large Green Circle}"
    elif final_score >= 60:
        return "dark_orange", "\N{Large Orange Circle}"
    elif final_score >= 45:
        return "yellow", "\N{Large Yellow Circle}"
    else:
        return"red", "\N{Large Red Circle}"


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
        return None

    return data

# Part 2:  Recipe Search and match
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
        console.print("[red]Invalid choice. Try again.[/red]")

# Part 3: Dietary Preference Collector
def dietary_preference():
    """Collect dietary filters from the user."""
    dietrary_preference = input("\nDo you have any dietary preferences? Type 'y' for yes, anything else for no.\n")
    if dietrary_preference.lower() == "y":
        console.print("\nDietary filters (optional). Type 'y' for yes, anything else for no.")
        preferences = {
            "vegan": {
                "enabled": input("Vegan? (y/n): ").lower() == "y", # we ruturn True if the user types y, False otherwise
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
    additives_db = {} # dictonary of dictonaries
    # Load additives
    with open('additives.csv', mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["additive"].strip().lower() # we create a dictionary where: the key is the additive name, the value is another dictionary with its details
            additives_db[name] = {
            "category":   row["category"].strip(),
            "health_concern": row["health_concern"].strip(),
            "grade": int(row["grade"]) if row["grade"].strip() else 0,
            "safety_label": row["safety_label"].strip()
            }
    return additives_db

# Step 5: Processed food score
def create_score(recipe, additives_db):
    """Score recipe based on ultra-processed additives found."""
    # grab the list of the ingredients
    raw_ingredients = recipe.get("Ingredient_List", "") or ""
    raw_ingredients = raw_ingredients.lower()

    # for each matched additive reduce the score by 5 points (max score is 100)
    # create a list of the additive present in the recipe and store them (we'll print them later)
    recipe_score = 100
    additives_found = []

    for additive, info in additives_db.items(): # additive is the Key, info is the value (the inner dictionary with category, health_concern and grade)
        if additive in raw_ingredients:    # compare each ingredeint with the additives disctonary to see if any of the ingredient is present
            grade = info["grade"]
            recipe_score -= grade
            additives_found.append({
                "name":       additive,
                "category":   info["category"],
                "health_concern": info["health_concern"],
                "grade": grade,
                "safety_label": info["safety_label"]
            })

    recipe_score = max(0, recipe_score) # the score cannot go below 0

    return {"score": recipe_score, "additives_found": additives_found,}

# Step 6: create a class to store the resiult + score of each searched recipe,
class ScoredRecipe:
    """ Create a class to store the resiult + score of each searched recipe,
    so that we can create a history andcompare them later, ans use it to print
    the report card and the comparision table in a more organized way.
    We use this clas in main() to create an entry for each searched recipe a
    nd store it in the history list; in print_report() to print the report card;
    and in print_comparison() to print the comparision table."""

    def __init__(self, huds_data, final_score):
        self.name = huds_data.get("Recipe_Name")
        self.final_score = final_score["score"]
        self.additives = final_score["additives_found"]
        self.protein = huds_data.get("Protein", "N/A")
        self.sodium = huds_data.get("Sodium", "N/A")
        self.dietary_fiber = huds_data.get("Dietary_Fiber", "N/A")
        self.data = huds_data # store the full data for comparision table

    def __str__(self):
        return f"{self.name:<45}  SCORE: {self.final_score} / 100"


# Step 7: Report Card
def print_report(entry, preferences):
    """
    Print a report card using rich.
    Called from main() after every successful search.
    """
    recipe_name = entry.name
    calories = entry.data.get("Calories",   "N/A")
    allergens = clean_trailing(entry.data.get("Allergens", "") or "")
    ingredients_list = entry.data.get('Ingredient_List') or "N/A"
    nutrition_score = entry.final_score
    additives_found = entry.additives

    # Header
    console.print()
    text = Text(justify="center")
    text.append(recipe_name, style="bold blue_violet")
    text.append(f"\nCalories: {calories} kcal per serving", style="white")
    console.print(Panel(Align.center(text),
        title = "[bold white]HUDS NUTRITION REPORT CARD[/bold white]",
        border_style = "cyan",
        padding= (1, 4),
        width = 55
    ))

    # Main output
    max_len = len("Ingredients:")
    console.print(textwrap.fill(ingredients_list.strip(" \t\n,( "), width=80, initial_indent="Ingredients: ",subsequent_indent=" " * 13))
    console.print(f"{'Allergens:':<{max_len}} {allergens}")

    # Dietary preferences
    banned_ingredients = []
    if preferences:
        for key, info in preferences.items(): # I could also use - to say that we ignore the key
            if info["enabled"]:
                for ingredient in get_wordlist(ingredients_list, remove_stopwords=False):
                    if ingredient in info["forbidden"]:
                        banned_ingredients.append(ingredient)
    if banned_ingredients:
        console.print(f"[bold deep_pink4]\nThis recipe contains the following ingredients that may not align with :\n [/bold deep_pink4]"
                      f"[deep_pink4]{', '.join(item.capitalize() for item in set(banned_ingredients))}[/deep_pink4]")

    # Additives table
    console.print()
    has_health_concerns = False
    if additives_found:
        table = Table(
            title        = "⛔ Ultra-Processed Additives Found",
            box          = box.ROUNDED,
            border_style = "red",
            header_style = "bold red",
            show_lines   = True,)
        table.add_column("Additive",style="white", min_width=28)
        table.add_column("Purpose", style="yellow",min_width=18)
        if any(item["health_concern"] for item in additives_found):
            table.add_column("Health Concern", style="white", min_width=25)
            has_health_concerns = True
        table.add_column("Safety Label", style="blue",min_width=18)

        for item in additives_found:
            if has_health_concerns:
                table.add_row(
                    item["name"].title(),
                    item["category"],
                    item["health_concern"],
                    item["safety_label"],)
            else:
                table.add_row(
                    item["name"],
                    item["category"],
                    item["safety_label"],)

        console.print(table)

    else:
        console.print(Panel(
            "✅ [bold green]No ultra-processed additives found![/bold green]",
            border_style = "green",
        ))

    # Score Bar
    score_color, score_icon = score_color_icon(nutrition_score)
    filled = int((nutrition_score / 100) * 30)
    bar = "█" * filled + "░" * (30 - filled)

    console.print(
        f"\n  {score_icon}  [bold]Nutrition Score[/bold]   "
        f"[{score_color}][{bar}][/{score_color}]   "
        f"[bold {score_color}]{nutrition_score} / 100[/bold {score_color}]"
    )
    console.print()

# Step 8: Comparison Table
def print_comparison(chosen, choice):
    """Print a side-by-side comparison table of all searched recipes."""

    table = Table(
        title = "Recipe Comparison",
        box = box.ROUNDED,
        border_style = "deep_pink3",
        header_style = "bold deep_pink3",
        show_lines = True,)

    table.add_column("Recipe", style="white",  min_width=35)
    table.add_column("Score", style="white",  min_width=10)
    if choice == "A":
        table.add_column("Additives Found", style="white",  min_width=16)
    elif choice == "P":
        table.add_column("Protein (g)", style="white",  min_width=12)
    elif choice == "S":
        table.add_column("Sodium (mg)", style="white",  min_width=12)
    elif choice == "F":
        table.add_column("Dietary Fiber (g)", style="white",  min_width=18)

    for entry in chosen:
        color, icon = score_color_icon(entry.final_score)
        score_str = f"{icon} [{color}]{entry.final_score}/100[/{color}]"
        if choice == "A":
            table.add_row(entry.name,score_str,str(len(entry.additives)),)
        elif choice == "P":
            table.add_row(entry.name,score_str,entry.protein)
        elif choice == "S":
            table.add_row(entry.name,score_str,entry.sodium)
        elif choice == "F":
            table.add_row(entry.name,score_str,entry.dietary_fiber)

    console.print(table)

    # Highlight the best option
    if choice == "A":
        best = max(chosen, key=lambda entry: entry.final_score) # max find the item in history with the max final_score
        console.print(
            f"\n  \N{Trophy} [bold green]Best option: "
            f"{best.name} (Score: {best.final_score}/100)[/bold green]\n")
    elif choice == "P":
        best = max(chosen, key=lambda entry: entry.protein if isinstance(entry.protein, (int, float)) else 0) # Isinstance (object, type) evaluates to True if r.protein is an integer or float, else False.
        console.print(
            f"\n  \N{Trophy} [bold green]Option with more protein: "
            f"{best.name} (Protein: {best.protein} grams)[/bold green]\n")
    elif choice == "S":
        best = min(chosen, key=lambda entry: entry.sodium if isinstance(entry.sodium, (int, float)) else float('inf')) # Isinstance (object, type) evaluates to True if r.calories is an integer or float, else False. If it's not a number, we treat it as infinity so it won't be chosen as the best option.
        console.print(
            f"\n  \N{Trophy} [bold green]Option with less sodium: "
            f"{best.name} (Sodium: {best.sodium})[/bold green]\n")
    elif choice == "F":
        best = max(chosen, key=lambda entry: entry.data.get("Dietary_Fiber", 0) if isinstance(entry.data.get("Dietary_Fiber", 0), (int, float)) else 0)
        console.print(
            f"\n  \N{Trophy} [bold green]Option with more dietary fiber: "
            f"{best.name} (Dietary Fiber: {best.data.get('Dietary_Fiber', 'N/A')} grams)[/bold green]\n")

# Step 0: Main Loop
def main():
    # Welcome message
    # Header
    text = Text(justify="center")
    text.append("HUDS Nutrition Scorer", style="bold plum2")
    text.append("\nMarta Amani  ·  Final Project CS32", style="dim white")
    console.print(Panel(
        text,
        border_style = "plum2",
        padding      = (1, 4),
        width        = 45
    ))


    # Step 4
    additives_db = load_data()
    preferences = dietary_preference()
    history = [] # store the history of searched recipes in this session

    #prefereces = dietary_preference()

    while True:
        search = input("Which recipe would you like to search? (or 'q' to quit): ").strip().lower() # we strip so that we can still look for a match even
                                                                                            # if the user added a space at the beginnig by accident
        if search.lower() == "q" or search.lower() == "quit" or search.lower() == "no" or search.lower() == "n"  :
            console.print("\nGoodbye! ")
            break

        data = connection(search)

        if not data:
            console.print(f"[red]Could not connect to the HUDS server. Please try again.[/red]")
            continue # API failed

        huds_data = find_recipe(search, data)

        if not huds_data:
            console.print(f'[red]No recipe found for "{search}". Please try another search term.[/red]')
            continue # no recipe found

        final_score = create_score(huds_data, additives_db)
        entry = ScoredRecipe(huds_data, final_score)
        print_report(entry, preferences)
        history.append(entry)

        if len(history) >= 2:
            while True:
                comparision_setup = input("\nWould you like to compare all searched recipes so far Type 'y' for yes, anything else for no.\n")
                if comparision_setup.lower() != "y":
                    break
                # Show numbered list of searched recipes. Let the user chose
                if len(history) > 2:
                    chosen = [] # if there are more than 2 recipes, the user choose which ones to compare
                    console.print("\nRecipes searched so far:")
                    for i, entry in enumerate(history):
                        console.print(f"  {i+1}. {entry.name}")
                    # The student/user decides which to compare
                    while True:
                        choice_compare = input("\nEnter the number of the recipes you want to compare (e.g. 1,2, etc.) ").strip()
                        choice_compare_index = choice_compare.split(",")

                        if not all(index.strip().isdigit() and 1 <= int(index.strip()) <= len(history)
                                   for index in choice_compare_index):
                            console.print("[red]Invalid input. Please enter valid number between 1 and {len(history)}[/red]")
                            continue

                        chosen = [] # reset after each attempt
                        for index in choice_compare_index:
                            chosen.append(history[int(index.strip())-1])
                        if len(chosen) >= 2:
                            break
                        console.print("[red]Please enter at least two valid numbers separated by commas.[/red]")
                else:
                    chosen = history # by default we compare all the searched recipes

                # Ask the user what they want to compare
                while True:
                    choice = input("\nWhat would you like to compare? Type 'A' for additives found, 'P' for Protein, 'S' for Sodium, 'F' for Dietary Fiber.\n").strip().upper()
                    if choice in ["A", "P", "S", "F"]:
                        break
                    console.print("[red]Invalid choice. Please enter 'A', 'P', 'S', or 'F'.[/red]")
                print_comparison(chosen, choice)

if __name__ == "__main__":
    main()
