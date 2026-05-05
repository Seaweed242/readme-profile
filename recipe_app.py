import json
import os
import random
from google import genai
from google.genai import types

# ==========================================
# 1. Configuration & Setup
# ==========================================
DATA_FILE = 'recipes.json'

# my hardcoded API Key
MY_API_KEY = "Your_API_Key_Here"

try:
    
    client = genai.Client(
        api_key=MY_API_KEY,
        http_options=types.HttpOptions(api_version='v1')
    )
except Exception as e:
    print(f"Error initializing AI client: {e}")
    client = None

# Default data 
DEFAULT_DATA = {
    "High Protein": [
        {"name": "Chicken & Rice", "ingredients": ["chicken breast", "rice", "broccoli", "soy sauce"]},
        {"name": "Egg Scramble", "ingredients": ["eggs", "spinach", "cheese", "butter"]}
    ],
    "Low Calorie": [
        {"name": "Zucchini Noodles", "ingredients": ["zucchini", "tomato sauce", "garlic", "parmesan"]}
    ],
    "Quick Meals": [
        {"name": "Peanut Butter Toast", "ingredients": ["bread", "peanut butter", "banana"]},
        {"name": "Quesadilla", "ingredients": ["tortilla", "cheese", "salsa"]}
    ]
}

# ==========================================
# 2. Data Management (Load/Save)
# ==========================================
def load_data():
    """Loads recipe data from a JSON file. Creates it if it doesn't exist."""
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA
    
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("Error reading data file. Loading defaults.")
        return DEFAULT_DATA

def save_data(data):
    """Saves the current recipe data dictionary to a JSON file."""
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# ==========================================
# 3. Core Functions
# ==========================================
def view_categories(data):
    """Displays all categories and the recipes inside them."""
    print("\n--- Available Categories & Recipes ---")
    if not data:
        print("No recipes found! Try adding some.")
        return

    for category, recipes in data.items():
        print(f"\n[{category}]")
        for idx, recipe in enumerate(recipes, 1):
            ingredients_str = ", ".join(recipe['ingredients'])
            print(f"  {idx}. {recipe['name']} (Ingredients: {ingredients_str})")
    print("--------------------------------------")

def generate_random_recipe_api():
    """Fetches a brand new recipe using Gemini, with optional user keywords."""
    print("\n--- AI Recipe Generator ---")
    
    # 1. Ask the user for keywords
    print("Want something specific? (e.g., 'high protein', 'vegan', 'sugar free')")
    keywords = input("Enter keywords OR just press Enter for completely random: ").strip()
    
    print("\nCooking up your recipe using AI...")
    
    if not client:
        print("Error: AI client not initialized.")
        return

    try:
        # 2. Adjust the prompt based on what the user typed
        if keywords:
            focus_instruction = f"The recipe MUST focus on these keywords/dietary needs: {keywords}."
        else:
            focus_instruction = "The recipe should be completely random."

        # 3. Build the final prompt
        prompt = (
            f"You are a helpful culinary assistant. {focus_instruction} "
            "Generate a delicious and easy-to-make recipe. Format your response strictly like this:\n"
            "Recipe Name: [Name]\n"
            "Category: [Category]\n"
            "Ingredients: [Comma separated list]\n"
            "Instructions: [Brief 2-3 sentence instructions]"
        )
        
        # model works for this version and is compatable with free thing
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", 
            contents=prompt
        )
        
        print("\n✨ --- AI Generated Recipe --- ✨")
        print(response.text)
        print("✨ --------------------------- ✨")
        
    except Exception as e:
        print(f"\n[AI Error]: {e}")

def ingredient_match(data):
    """Suggests recipes based on user-provided ingredients."""
    print("\n--- Ingredient Matcher ---")
    user_input = input("Enter the ingredients you have (separated by commas): ").strip()
    
    if not user_input:
        print("Input cannot be empty. Please try again.")
        return
        
    user_ingredients = [item.strip().lower() for item in user_input.split(',')]
    matches_found = False
    print("\nHere is what you can make:")
    
    for category, recipes in data.items():
        for recipe in recipes:
            recipe_ingredients = [ing.lower() for ing in recipe['ingredients']]
            matching = set(user_ingredients).intersection(set(recipe_ingredients))
            missing = set(recipe_ingredients).difference(set(user_ingredients))
            
            if matching:
                matches_found = True
                print(f"\n- {recipe['name']} (from '{category}')")
                print(f"  You have: {', '.join(matching)}")
                if missing:
                    print(f"  Missing: {', '.join(missing)}")
                else:
                    print("  🔥 You have ALL the ingredients!")

    if not matches_found:
        print("No matching recipes found for those ingredients.")

def add_recipe(data):
    """Allows the user to input a new recipe and saves it."""
    print("\n--- Add a New Recipe ---")
    name = input("Recipe Name: ").strip()
    if not name: return
        
    category = input("Category: ").strip()
    if not category: return
        
    ingredients_input = input("Ingredients (comma separated): ").strip()
    if not ingredients_input: return
        
    ingredients_list = [item.strip() for item in ingredients_input.split(',')]
    
    if category not in data:
        data[category] = []
        
    new_recipe = {"name": name, "ingredients": ingredients_list}
    data[category].append(new_recipe)
    save_data(data)
    print(f"\n✅ Success! '{name}' added.")

# ==========================================
# 4. Program Flow & Menu
# ==========================================
def display_menu():
    print("\n" + "="*30)
    print("   🍽️  RECIPE DECIDER 3000   ")
    print("="*30)
    print("1. View Categories & Recipes")
    print("2. Generate AI Recipe (With Keywords)")
    print("3. Match by Ingredients")
    print("4. Add Your Own Recipe")
    print("5. Exit")
    print("="*30)

def main():
    recipe_data = load_data()
    
    while True:
        display_menu()
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == '1':
            view_categories(recipe_data)
        elif choice == '2':
            generate_random_recipe_api()
        elif choice == '3':
            ingredient_match(recipe_data)
        elif choice == '4':
            add_recipe(recipe_data)
        elif choice == '5':
            print("Saving... Goodbye!")
            save_data(recipe_data)
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()

# If i need to change the API key, i can just change the value of MY_API_KEY at the top of the file.
# run command in terminal: $env:GEMINI_API_KEY="your_actual_key_here"
# in order to run the program the command is: python recipe_app.py
# if trying to download libary run this command: python -m pip install google-genai
# make sure python is downloaded to Vs code and to computer 