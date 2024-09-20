import json
import streamlit as st
import google.generativeai as genai
import random
from datetime import datetime
from append_to_sheet import append_to_sheet

diet_plans = """FAT LOSS VEGETARIAN LCD: A vegetarian fat-loss diet with balanced options for breakfast, lunch, 
evening meal, and dinner focused on low-carbohydrate intake.\n\n FAT LOSS Eggatarian LCD: An egg-based fat-loss diet 
plan offering choices between vegetarian and egg-based meals with low-carb options for all meals.\n\n FAT LOSS 
Non-vegetarian LCD: A fat-loss diet incorporating lean meats like chicken and fish alongside vegetarian options to 
manage carbohydrate intake.\n\n FAT LOSS VEGETARIAN (15 days): A short-term vegetarian fat-loss plan with minimal meal 
variety, focusing on cooked veggies, salad, and paneer or curd.\n\n FAT LOSS Eggatarian (15 days): A 15-day eggatarian 
fat-loss plan emphasizing vegetable and egg-based meals with a focus on healthy fats like coconut oil.\n\n FAT LOSS 
Non-vegetarian (15 days): A non-vegetarian fat-loss diet for 15 days, including lean meats, veggies, and coconut oil 
for sustainable fat loss.\n\n Keto Non-vegetarian: A high-fat, low-carb ketogenic plan using meats, eggs, and healthy 
oils to trigger fat loss while limiting carbohydrate intake.\n\n Keto Vegetarian: A vegetarian ketogenic plan with 
paneer, cheese, and healthy fats to maintain ketosis while including occasional lentil-based meals.\n\n Weight Gain 
Non-vegetarian: A non-vegetarian weight-gain diet with calorie-dense foods like parathas, meats, and whey protein to 
encourage muscle growth.\n\n Weight Gain Vegetarian: A vegetarian weight-gain plan rich in healthy fats, proteins, 
and high-calorie meals like paneer, parathas, and oats for mass gain.\n\n Weight Gain Eggatarian: An eggatarian 
weight-gain diet featuring a mix of eggs, paneer, and calorie-dense foods to boost muscle mass and overall weight.\n\n"""

genai.configure(api_key=st.secrets["API_KEY"])
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

with open("plan.json", 'r') as f:
    plans = json.load(f)

st.title("Match-a🍵 - The Diet Plan Recommender")

info = st.button("💡Info about the diet plans❓")
if info:
    st.info(diet_plans)
    
rand = st.button("I'm Feeling Lucky✨")
if rand:
    st.write(plans[random.choice(list(plans.keys()))])

def fill_form():
    # Define options for select boxes
    status = False
    genders = ["Male", "Female", "Other"]
    activity_levels = ["Low", "Moderate", "High", "Active"]
    health_goals = ["Weight Loss", "Muscle Gain", "Weight Maintenance", "Heart Health", "Fat Loss"]
    dietary_preferences = ['FAT LOSS VEGETARIAN LCD', 'FAT LOSS EGGETARIAN LCD', 'FAT LOSS NON VEGETARIAN LCD',
                           'FAT LOSS VEGETARIAN 15 days', 'FAT LOSS EGGETARIAN 15 days',
                           'FAT LOSS NON VEGETARIAN 15 days',
                           'Keto Non Vegetarian Plan', 'Keto Vegetarian Plan', 'Weight Gain Non Vegetarian',
                           'Weight Gain Vegetarian', 'Weight Gain Eggetarian']

    # Create the form
    with st.form(key='user_form', border=False,clear_on_submit=True):
        name = st.text_input(label='Name')
        age = st.number_input("age", min_value=15, max_value=120)
        gender = st.selectbox("gender", genders, index=None)
        weight = st.number_input("Weight (kg)", min_value=40.0, max_value=200.0)
        height = st.number_input("Height (cm)", min_value=100, max_value=250)
        activity_level = st.selectbox("Activity Level", activity_levels, index=None)
        dietary_preference = st.selectbox("Dietary Preference", dietary_preferences, index=None)
        health_goal = st.selectbox("Health Goal", health_goals, index=None)

        submit_button = st.form_submit_button(label='Submit')

    if submit_button:
        # Concatenate values into a space-separated string
        status = True
        user_info = (f"{name} {age} {gender} {weight} {height} {activity_level} {dietary_preference} {health_goal} "
                     f"{str(datetime.now())}")
        append_to_sheet(user_info.split(" "))
        return user_info, status, dietary_preference
    else:
        return "", status, ""


def recommendations():
    """Prompt AI and gemini will retrieve and rank dishes"""
    _, status, dietary_preference = fill_form()
    if dietary_preference != "":
        res = model.generate_content([f"Restructure {plans[dietary_preference]} properly with suitabl bold headings etc."])
        st.write(res.text)


recommendations()

