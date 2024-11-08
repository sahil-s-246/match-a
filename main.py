import json
import streamlit as st
import google.generativeai as genai
import random
from datetime import datetime
from append_to_sheet import append_to_sheet
import tempfile
from markdown_pdf import MarkdownPdf, Section
import os
from google.api_core.exceptions import ResourceExhausted

def create_pdf(content):
    pdf = MarkdownPdf(toc_level=1)

    pdf.add_section(Section(f"{content}"))
    pdf.meta["title"] = "Diet Plan"
    pdf.meta["author"] = "Sahil S"
    temp_dir = tempfile.mkdtemp()
    temp_pdf_path = os.path.join(temp_dir, 'output.pdf')

    pdf.save(temp_pdf_path)

    return temp_pdf_path


def cleanup_pdf(pdf_path):
    try:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            return True
    except Exception as e:
        print(f"Error deleting temporary PDF: {e}")
        return False


spnotes = """
---
SPECIAL NOTES
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
 ---

KETO Notes
1) Have salt lime water 1lit/day
2) use sugar free like stevia to take care of sweet tooth
3) In between snacking can include Avocado or its juice or pumpkin seeds 
4) You can make roties with almond flour and flaxseed powder 
5) fruits.. strawberry or raspberry or blueberry or avacado or cherries
6) vegetable.. all green leafy vegetables, salad vegetable, cucumber,tomato, mushroom, capsicum, bell paper,
 cherry tomato, cauliflower, cabbage, broccoli, French beans, ladies finger, pumpkin, raddish, carrot
"""

diet_plans = """FAT LOSS VEGETARIAN Low Carb Diet: A vegetarian fat-loss diet with balanced options for breakfast, lunch, 
evening meal, and dinner focused on low-carbohydrate intake.\n\n FAT LOSS Eggatarian Low Carb Diet: An egg-based fat-loss diet 
plan offering choices between vegetarian and egg-based meals with low-carb options for all meals.\n\n FAT LOSS 
Non-vegetarian Low Carb Diet: A fat-loss diet incorporating lean meats like chicken and fish alongside vegetarian options to 
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

st.warning("Please wait for a second after submission")


def fill_form():
    # Define options for select boxes
    status = False
    genders = ["Male", "Female"]
    activity_levels = ["Low", "Moderate", "High", "Active"]
    health_goals = ["Weight Loss", "Muscle Gain", "Weight Maintenance", "Heart Health", "Fat Loss"]
    dietary_preferences = ['FAT LOSS VEGETARIAN Low Carb Diet', 'FAT LOSS EGGETARIAN Low Carb Diet', 'FAT LOSS NON VEGETARIAN Low Carb Diet',
                           'FAT LOSS VEGETARIAN 15 days', 'FAT LOSS EGGETARIAN 15 days',
                           'FAT LOSS NON VEGETARIAN 15 days',
                           'Keto Non Vegetarian Plan', 'Keto Vegetarian Plan', 'Weight Gain Non Vegetarian',
                           'Weight Gain Vegetarian', 'Weight Gain Eggetarian']

    # Create the form
    with st.form(key='user_form', border=False, clear_on_submit=True):
        # Basic Information
        name = st.text_input(label='Name')
        email = st.text_input(label='Email')
        country = st.text_input(label='Country')
        contact = st.text_input(label='Contact')

        # Physical Attributes
        height = st.number_input("Height (cm)", min_value=100, max_value=250)
        weight = st.number_input("Weight (kg)", min_value=40.0, max_value=200.0)
        age = st.number_input("Age", min_value=15, max_value=120)
        gender = st.selectbox("Gender", genders, index=None)

        # Health and Lifestyle
        health_condition = st.text_input("Any Health Condition")
        lifestyle = st.selectbox("Lifestyle", ["Sedentary", "Moderately Active", "Very Active"])
        physical_activity = st.radio("Are you active in physical exercises?", ["Yes", "No"],index=1)
        if physical_activity == "Yes":
            activities = st.text_area("Please Mention the Activities")
            activity_days = st.number_input("How many days a week do you perform these activities?", min_value=0,
                                            max_value=7)

        # Dietary Preferences
        dietary_preference = st.radio("Dietary Preference", dietary_preferences, index=None)

        # Health Goals
        health_goal = st.selectbox("Target for Joining", ["Weight Loss", "Weight Gain", "Maintenance"], index=None)
        eating_timings = st.text_area("Current Eating Pattern Timings (e.g., Breakfast: 8 AM, Lunch: 1 PM, etc.)")

        # Submit Button
        submit_button = st.form_submit_button(label='Submit')

    if submit_button:
        # Concatenate values into a space-separated string
        status = True
        user_info = (f"{name} {age} {gender} {weight} {height} {dietary_preference} {health_goal} "
                     f"{str(datetime.now())}")
        append_to_sheet(user_info.split(" "))
        user_dict = {
            "name": name,
            "age": age,
            "gender": gender,
            "weight": weight,
            "height": height,
            "dietary_preference": dietary_preference,
            "health_goal": health_goal,
            "timestamp": datetime.now().isoformat()
        }
        return user_dict, status, dietary_preference, eating_timings
    else:
        return "", status, "", ""


def recommendations():
    """Prompt AI and gemini will provide the diet plan"""
    user_info, status, dietary_preference, eating_timings = fill_form()

    notes = ""
    keto = False

    if dietary_preference == "Keto Non Vegetarian Plan" or dietary_preference == "Keto Vegetarian Plan":
        keto = True
    if dietary_preference != "":
        with st.spinner("Loading..."):
            try:
                res = model.generate_content([f"Restructure {plans[dietary_preference]}"
                                              f" properly. Please provide a response in plain text without formatting "
                                              f"alpha numeric as far as possible"
                                              f"Split the meal content as per nutrtion for a balanced meal and list them"
                                              f" separately"
                                              f"For eg: Curry can be a balanced diet, but milk in combination with cereal"
                                              f" covers carbs from cereal, protein from milk etc. and don't put extra notes,"
                                              f" just the plan would suffice. Make a proper schedule according to "
                                              f"{eating_timings} and include the time in it."
                                              f" Don't use markdown only plain text"
                                              ])
                st.write(res.text)
            except KeyError:
                st.error("Please fill the dietary preference before submitting the form")
                return
            except ResourceExhausted:
                st.error("A lot of people are making requests at the moment. Please try in a few minute")
            except:
                st.error("Something went wrong. Please try again")
            if not keto:
                notes = spnotes
            else:
                notes = keto_notes
            result = f"{res.text}\n\n{notes}"
            temp = create_pdf(result)
            if user_info["name"] is None:
                user_info["name"] = "diet_plan"
            with open(temp, "rb") as file:
                download = st.download_button(label="Download Diet Plan PDF",
                                              data=file,
                                              file_name=f"{user_info["name"]}.pdf",
                                              mime="application/pdf")
            if download:
                cleanup_pdf(temp)

    else:
        st.warning("Please fill choose a diet plan and fill all the details as well")


if __name__ == "__main__":
    recommendations()
