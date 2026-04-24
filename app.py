"""
FINAL PROJECT - HUDS Nutrition Scorer - Marta Amani
Flask web application
"""

from flask import Flask, render_template, request
from FP import connection, find_recipe, dietary_preference, load_data, create_score
import os
from dotenv import load_dotenv

app = Flask(__name__)
additives_db = load_data()

@app.route("/", methods=["GET","POST"])
def index():
    """Show the search form."""
    return render_template("index.html")
    result = None
    error  = None
    query  = ""

    if request.method == "POST":
        query = request.form.get("recipe","").strip()
        data  = connection(query)
        if not data:
            error = "Could not reach the HUDS API. Please try again."
        else:
            recipe = find_recipe(query, data)
            if not recipe:
                error = f'No recipe found for "{query}". Try a different name.'
            else:
                score_data = create_score(recipe, additives_db)
                result = {
                    "name":        recipe.get("Recipe_Name",""),
                    "location":    recipe.get("Location_Name",""),
                    "meal":        recipe.get("Meal_Name",""),
                    "calories":    recipe.get("Calories","?"),
                    "allergens":   (recipe.get("Allergens") or "None").strip(", "),
                    "ingredients": re.sub(r'[\s,)(]+$','',
                                   recipe.get("Ingredient_List","")).strip(),
                    "score":       score_data["score"],
                    "score_color": score_color(score_data["score"]),
                    "additives":   score_data["additives_found"],
                }

    return render_template("index.html", result=result, error=error, query=query)

if __name__ == "__main__":
    app.run(debug=True)
