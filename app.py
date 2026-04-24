"""
FINAL PROJECT - HUDS Nutrition Scorer - Marta Amani
Flask web application
"""

from flask import Flask, render_template, request
from FP import connection, find_recipe, load_data, create_score
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
additives_db = load_data()

@app.route("/", methods=["GET"])
def index():
    """Show the search form."""
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    """Handle form submission and show results."""
    recipe_name = request.form.get("recipe_name", "").strip()
    vegan       = request.form.get("vegan")       == "on"
    gluten_free = request.form.get("gluten_free") == "on"
    nut_free    = request.form.get("nut_free")    == "on"

    # fetch and score
    data   = connection(recipe_name)
    recipe = find_recipe(recipe_name, data) if data else None

    if not recipe:
        return render_template(
            "index.html",
            error = f'No recipe found for "{recipe_name}"'
        )

    final_score = create_score(recipe, additives_db)

    # dietary warnings
    ingredients = (recipe.get("Ingredient_List") or "").lower()
    warnings    = []
    if vegan and any(w in ingredients for w in
                     ["meat","chicken","fish","egg","milk","cheese"]):
        warnings.append("⚠  Not vegan-friendly")
    if gluten_free and any(w in ingredients for w in
                           ["wheat","barley","rye","malt"]):
        warnings.append("⚠  Contains gluten")
    if nut_free and any(w in ingredients for w in
                        ["almond","walnut","cashew","peanut"]):
        warnings.append("⚠  Contains nuts")

    return render_template(
        "results.html",
        recipe      = recipe,
        final_score = final_score,
        warnings    = warnings,
    )


if __name__ == "__main__":
    app.run(debug=True)
