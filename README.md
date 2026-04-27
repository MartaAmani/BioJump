# BioJump - HUDS Nutrition Scorer
Final project for the class CS32 Spring 2026, at Harvard University.


## What This Project Does
This project analyzes the ingredients of the Harvard University Dining Services (HUDS) recipes using the Harvard Dining API. Given a dish name, the Python script creates a report card for each recipe, providing the user/students with the nutrition analysis and processing score of the dish.

The report card has two main components:

- **Processing Score**: based on the additives present in the recipes, categorized according to the NOVA classification system.

- **Nutrition Info**: displays nutrition values and ingredients for the recipe

The user/student interacts with the HUDS Nutrition Scorer through the terminal. The user/student is asked which recipe they would like to search. Then, after typing a recipe name, the program searches the HUDS database:
- if there is a recipe that exactly matches the input, then the report card for that recipe will be displayed;
- if there is not an exact match, then the possible matches are printed in the terminal, and the user/student is asked to select one based on its number in the list;
- if there is no match, the user is asked to input a different recipe name.

The program keeps a **session history** of every recipe search, and allows user/student to compare recipes.


## Structure
This project uses the Harvard Dining API, which requires a personal API key.
To obtain an API Key, Harvard students are required to go to https://portal.apis.huit.harvard.edu, then go to the API Catalog and search for "Dining API". After creating an app, students can obtain an API Key.

Then, in the codespace, create a file called .env, which allows storing sensitive information like the API_Key as key-value pairs, while keeping them out of the source code and not available to the public. The document .env.example shows the user the type of input required.

Then, I created a CSV file containing a list of ultra-processed additives used for scoring. The file has the following columns: additives, category, description.
Moreover, to help myself debug the code, through a function called debug.py, I created a file called HUDS_recipes.txt, containing all the recipes.

The Python code consists of several functions that flag ingredients, categorize them, and produce a visual image/chart with the summary of the analysis. The main task consists of parsing the ingredient and matching it against multiple databases (additives database). Moreover, the report card includes the creation of charts showing the distribution of the food nutrients, dietary flags, and a color-coded additive list.

To run the code, the user needs to type python3 FP.py

## External Sources and Citations

- List of ultra-processed additives in additives.csv is based on:

    https://www.cspi.org/page/chemical-cuisine-food-additive-safety-ratings

- Harvard Dining API:

    https://portal.apis.huit.harvard.edu/docs/ats-dining/1/overview


## Use of Generative AI
I used Claude (Anthropic) as a generative AI assistant throughout this project.
While the design of this project and the functions are entirely designed by me, the code for the report card, which exploits the Python library’s rich features, was partially imported from the output provided by generative AI. In particular, the structure and rich formatting syntax (Panel, Table, progress bar) were written with AI assistance. I adapted the output labels, colors, and layout to match my project's design and implemented the report card with more personalized features.

Moreover, generative AI provided explanations for the .env setup and .gitignore configuration.
