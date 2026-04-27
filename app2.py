import streamlit as st
from FP2 import (
    connection,
    find_recipe,
    create_score,
    load_data,
    score_color_icon,
)

additives_db = load_data()

st.title("🍽 HUDS Nutrition Scorer")
st.write("Marta Amani · Final Project CS32")

recipe_name = st.text_input("Search a recipe:")

if st.button("Search"):
    if not recipe_name.strip():
        st.warning("Please enter a recipe name.")
    else:
        with st.spinner("Searching HUDS..."):
            data = connection(recipe_name)

        if not data:
            st.error("Could not connect to HUDS. Please try again.")
        else:
            exact, partial = find_recipe(recipe_name, data)

            # Let user pick from partial matches in the browser
            if not exact and partial:
                names  = [r.get("Recipe_Name") for r in partial]
                choice = st.selectbox(
                    "No exact match. Did you mean one of these?", names
                )
                recipe = next(
                    r for r in partial if r.get("Recipe_Name") == choice
                )
            elif exact:
                recipe = exact
            else:
                st.error(f"No recipe found for '{recipe_name}'.")
                st.stop()

            # Score
            final_score = create_score(recipe, additives_db)
            score       = final_score["score"]
            color, icon = score_color_icon(score)

            # Report card
            st.header(recipe.get("Recipe_Name"))
            st.write(f"**Calories:** {recipe.get('Calories')} kcal")
            st.write(
                f"**Allergens:** {recipe.get('Allergens') or 'None listed'}"
            )
            st.metric("Nutrition Score", f"{score} / 100")
            st.progress(score / 100)

            # Additives
            if final_score["additives_found"]:
                st.error("⛔ Ultra-Processed Additives Found")
                st.dataframe(final_score["additives_found"])
            else:
                st.success("✅ No ultra-processed additives found!")
