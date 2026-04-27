import streamlit as st
from FP import (          # import from FP.py
    connection,
    find_recipe,
    create_score,
    load_data,
    score_color_icon,
)

# Load additives once at the start
additives_db = load_data()

# Header
st.title("🍽 HUDS Nutrition Scorer")
st.write("Marta Amani · Final Project CS32")

# Search
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
            recipe = find_recipe(recipe_name, data)

            if not recipe:
                st.error(f"No recipe found for '{recipe_name}'.")
            else:
                final_score = create_score(recipe, additives_db)
                score       = final_score["score"]
                color, icon = score_color_icon(score)

                # Report card
                st.header(recipe.get("Recipe_Name"))
                st.write(f"**Calories:** {recipe.get('Calories')} kcal")
                st.write(f"**Allergens:** {recipe.get('Allergens') or 'None listed'}")

                # Score
                st.metric("Nutrition Score", f"{score} / 100")
                st.progress(score / 100)

                # Additives table
                if final_score["additives_found"]:
                    st.error("⛔ Ultra-Processed Additives Found")
                    st.dataframe(final_score["additives_found"])
                else:
                    st.success("✅ No ultra-processed additives found!")

