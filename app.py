import os
import streamlit as st
import pandas as pd
import plotly.express as px

import preprocessor
import helper

# ---------------- PATH SETUP ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ATHLETE_PATH = os.path.join(BASE_DIR, "athlete_events.csv")
REGION_PATH = os.path.join(BASE_DIR, "noc_regions.csv")

# ---------------- LOAD DATA (CACHED) ----------------
@st.cache_data
def load_data():
    df = pd.read_csv(
        ATHLETE_PATH,
        encoding="latin1",
        engine="python",
        on_bad_lines="skip"
    )

    region_df = pd.read_csv(
        REGION_PATH,
        encoding="latin1",
        engine="python",
        on_bad_lines="skip"
    )

    df = preprocessor.preprocess(df, region_df)
    return df

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("Olympic Analysis")
user_menu = st.sidebar.radio(
    "Select an option",
    (
        "Medal Tally",
        "Overall Analysis",
        "Country-wise analysis",
        "Athletes-wise analysis"
    )
)

# ---------------- MEDAL TALLY ----------------
if user_menu == "Medal Tally":
    st.header("Medal Tally")

    years, country = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", country)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    if selected_year == "Overall" and selected_country == "Overall":
        st.title("Overall Tally")
    elif selected_year != "Overall" and selected_country == "Overall":
        st.title(f"Medal Tally in {selected_year} Olympics")
    elif selected_year == "Overall" and selected_country != "Overall":
        st.title(f"{selected_country} Overall Performance")
    else:
        st.title(f"{selected_country} performance in {selected_year} Olympics")

    st.table(medal_tally)

# ---------------- OVERALL ANALYSIS ----------------
if user_menu == "Overall Analysis":
    editions = df["Year"].nunique()
    cities = df["City"].nunique()
    sports = df["Sport"].nunique()
    events = df["Event"].nunique()
    athletes = df["Name"].nunique()
    nations = df["region"].nunique()

    st.title("Top Statistics")

    col1, col2, col3 = st.columns(3)
    col1.metric("Editions", editions)
    col2.metric("Hosts", cities)
    col3.metric("Sports", sports)

    col1, col2, col3 = st.columns(3)
    col1.metric("Events", events)
    col2.metric("Nations", nations)
    col3.metric("Athletes", athletes)

    nations_over_time = helper.participating_nations_over_time(df)
    fig = px.line(
        nations_over_time,
        x="Year",
        y="count",
        title="Participating Nations Over Time"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- COUNTRY-WISE ANALYSIS ----------------
if user_menu == "Country-wise analysis":
    st.header("Country-wise Analysis")

    country_list = sorted(df["region"].dropna().unique())
    selected_country = st.selectbox("Select Country", country_list)

    medals_per_year = helper.country_medals_over_time(df, selected_country)

    fig = px.line(
        medals_per_year,
        x="Year",
        y="Medal",
        title=f"Medals of {selected_country} Over Time"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- ATHLETES ANALYSIS ----------------
if user_menu == "Athletes-wise analysis":
    st.header("Athletes Analysis")

    fig = helper.age_distribution(df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)



