# app.py
import streamlit as st

st.title("🍽 HUDS Nutrition Scorer")
st.write("Marta Amani · Final Project CS32")

recipe_name = st.text_input("Search a recipe:")

if st.button("Search"):
    with st.spinner("Searching..."):
        data        = connection(recipe_name)
        recipe      = find_recipe(recipe_name, data)
        final_score = create_score(recipe, additives_db)
        score       = final_score["score"]
        color, icon = score_color_icon(score)

    # Report card
    st.header(recipe.get("Recipe_Name"))
    st.metric("Nutrition Score", f"{score}/100")
    st.progress(score / 100)   # ← automatic progress bar!

    # Additives table
    if final_score["additives_found"]:
        st.error("⛔ Ultra-Processed Additives Found")
        st.dataframe(final_score["additives_found"])  # ← automatic table!
    else:
        st.success("✅ No ultra-processed additives found!")
