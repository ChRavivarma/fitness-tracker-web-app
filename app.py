import streamlit as st
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import time
import os
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# Load datasets
calories = pd.read_csv("calories.csv")
exercise = pd.read_csv("exercise.csv")

# Merge datasets
exercise_df = exercise.merge(calories, on="User_ID")
exercise_df.drop(columns=["User_ID"], inplace=True)

# Calculate BMI
exercise_df["BMI"] = exercise_df["Weight"] / ((exercise_df["Height"] / 100) ** 2)
exercise_df = exercise_df.round(2)

# Sidebar Inputs
st.sidebar.header("User Input Parameters")
activity_type = st.sidebar.selectbox("Activity Type", ["Walking", "Running", "Cycling", "Swimming"])
steps = st.sidebar.number_input("Steps Taken", min_value=0, step=100)
age = st.sidebar.slider("Age", 10, 100, 30)
bmi = st.sidebar.slider("BMI", 15, 40, 20)
duration = st.sidebar.slider("Duration (min)", 0, 60, 30)
heart_rate = st.sidebar.slider("Heart Rate", 60, 180, 90)
body_temp = st.sidebar.slider("Body Temperature (C)", 36.0, 42.0, 37.5, step=0.1)
gender_button = st.sidebar.radio("Gender", ("Male", "Female"))

gender = 1 if gender_button == "Male" else 0

# Prepare user data
data_model = {
    "Age": age,
    "BMI": bmi,
    "Duration": duration,
    "Heart_Rate": heart_rate,
    "Body_Temp": body_temp,
    "Gender_male": gender,
    "Steps": steps
}
df = pd.DataFrame(data_model, index=[0])

# Train Random Forest Model
# Convert Gender to numeric (0 for Female, 1 for Male)
exercise_df["Gender"] = exercise_df["Gender"].map({"male": 1, "female": 0})

# Prepare training data
X = exercise_df.drop(columns=["Calories"])
y = exercise_df["Calories"]
random_reg = RandomForestRegressor(n_estimators=100, max_depth=6)
random_reg.fit(X, y)

# Ensure input data matches training columns
df = df.reindex(columns=X.columns, fill_value=0)

# Predict calories
prediction = random_reg.predict(df)

# Display Prediction
st.header("Calories Burned")
fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = prediction[0],
    title = {"text": "Calories Burned"},
    gauge = {"axis": {"range": [0, 1000]}}
))
st.plotly_chart(fig)

# Recovery Time Estimate
if heart_rate > 140:
    recovery_time = "8-12 hours"
elif heart_rate > 120:
    recovery_time = "4-8 hours"
else:
    recovery_time = "1-4 hours"
st.write(f"⏳ Estimated Recovery Time: {recovery_time}")

# Hydration Recommendation
water_intake = round(duration * 0.2, 2)
st.write(f"💧 Recommended Water Intake: {water_intake} L")

# Define progress file
progress_file = "progress.csv"

# Append new data
new_entry = pd.DataFrame({"Day": [time.strftime("%a")], "Calories": [round(prediction[0], 2)]})

# Check if the file exists
if os.path.exists(progress_file):
    progress_df = pd.read_csv(progress_file)
    progress_df = pd.concat([progress_df, new_entry], ignore_index=True)
else:
    progress_df = new_entry

# Keep only the latest 7 days of data
progress_df = progress_df.tail(7)

# Save progress
progress_df.to_csv(progress_file, index=False)

# Weekly Progress Visualization
st.header("📈 Weekly Progress")
if os.path.exists(progress_file):
    progress_df = pd.read_csv(progress_file)
    progress_df.set_index("Day", inplace=True)  # Set 'Day' as index

# Ensure only numeric values are used in the heatmap
    numeric_df = progress_df.select_dtypes(include=["number"])

# Now plot the heatmap
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.heatmap(numeric_df, annot=True, cmap="coolwarm", ax=ax)

    st.pyplot(fig)
else:
    st.write("No progress data available yet. Start tracking today!")