import json
import streamlit as st
import google.generativeai as genai
import random
from datetime import datetime
from append_to_sheet import append_to_sheet
import tempfile
from fpdf import FPDF


def create_pdf(content):
    """Function to create PDF """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in content.split("\n"):
        pdf.cell(0, 5, txt=line, ln=True, align='L')

    # Create a temporary file
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_pdf.name)

    return temp_pdf.name


def clear_temp_file(file_path):
    """Function to clear the contents of the file"""
    with open(file_path, 'w') as temp_file:
        temp_file.write('')  # Overwrite with an empty string


spnotes = """
special Notes..
1) Avoid fruits after 1st meal
2) In between workout include at least 1lit salt lime or agal water
3)Can include without sugar green tea or black tea or black coffee
4) water.. 4-5lit/day

List To Include..
All green leafy vegetables like palak, methi, amarnath,( aalu) colocasia, chawali
bhindi, capsicum, dudhi, turai, parwar, Karla, baigan, gavar, papdi, olives, onions, broccoli, mushroom
salad.. cucumber, tomato, radish (mula), cabbage, lettuce, celery,
Almonds, walnuts, 

Avoid List...
corn flakes, maida, potato/peas/ carrot stuffed paratha 
poha,idli,dosa,white rice,sheera
fruits salad, banana, mango, dates, chiku
white sugar, honey, jaggary, icecream, chocolate, gellies, jam 
bakery products
dalda, margarine, safflower, sunflower oil
"""
keto_notes = """
Keto special notes..
1) Have salt lime water 1lit/day
2) use sugar free like stevia to take care of sweet tooth
3) In between snacking can include Avocado or its juice or pumpkin seeds 
4) You can make roties with almond flour and flaxseed powder 
5) fruits.. strawberry or raspberry or blueberry or avacado or cherries
6) vegetable.. all green leafy vegetables, salad vegetable, cucumber,tomato, mushroom, capsicum, bell paper,
 cherry tomato, cauliflower, cabbage, broccoli, French beans, ladies finger, pumpkin, raddish, carrot
"""

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
st.image("assets/B2B-Logo.png")

st.title("Match-a🍵 - The Diet Plan Recommender")

info = st.button("💡Info about the diet plans❓")
if info:
    st.info(diet_plans)

rand = st.button("I'm Feeling Lucky✨")
if rand:
    st.write(plans[random.choice(list(plans.keys()))])
st.warning("Please wait for a second after submission")

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
    with st.form(key='user_form', border=False, clear_on_submit=True):
        name = st.text_input(label='Name')
        age = st.number_input("age", min_value=15, max_value=120)
        gender = st.selectbox("gender", genders, index=None)
        weight = st.number_input("Weight (kg)", min_value=40.0, max_value=200.0)
        height = st.number_input("Height (cm)", min_value=100, max_value=250)
        activity_level = st.selectbox("Activity Level", activity_levels, index=None)
        dietary_preference = st.radio("Dietary Preference", dietary_preferences, index=None)
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
    """Prompt AI and gemini will provide the diet plan"""
    _, status, dietary_preference = fill_form()
    notes = ""
    keto = False
    if dietary_preference == "Keto Non Vegetarian Plan" or dietary_preference == "Keto Vegetarian Plan":
        keto = True
    if dietary_preference != "":
        with st.spinner("Loading..."):
            res = model.generate_content([f"Restructure {plans[dietary_preference]}"
                                          f" properly with suitable format in plain text, not md"
                                          f"Split the meal content as per nutrtion for a balanced meal and list them"
                                          f" separately"
                                          f"For eg: Curry can be a balanced diet, but milk in combination with cereal"
                                          f" covers carbs from cereal, protein from milk etc. and don't put extra notes,"
                                          f" just the plan would suffice"])
            st.write(res.text)
            if not keto:
                notes = spnotes
            else:
                notes = keto_notes
            result = f"{res.text}\n\n{notes}"
            temp = create_pdf(result)
            with open(temp, "rb") as file:
                download = st.download_button(label="Download Diet Plan PDF",
                                              data=file,
                                              file_name="diet_plan.pdf",
                                              mime="application/pdf")
            if download:
                clear_temp_file(temp)


if __name__ == "__main__":
    recommendations()
