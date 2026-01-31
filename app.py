import streamlit as st
import pandas as pd
import preprocessor,helper
from helper import fetch_medal_tally

# import matplotlib.pyplot as plt
# import seaborn as sns
import plotly.express as px
# LOAD DATA FIRST
df = pd.read_csv("athlete_events.csv")
region_df = pd.read_csv("noc_regions.csv")
df=preprocessor.preprocess(df,region_df)
st.sidebar.title("Olympic Analysis")
user_menu=st.sidebar.radio(
    "Select an option",
    ("Medal Tally","Overall Analysis","Country-wise analysis","Athletes-wise analysis")
)



if user_menu=="Medal Tally":
    st.header("Medal Tally")
    years,country=helper.country_year_list(df)
    selected_year=st.sidebar.selectbox("Select Year",years,key="medal_year")
    selected_country = st.sidebar.selectbox("Select Country",country,key="medal_country")
    medal_tally=helper.fetch_medal_tally(df,selected_year,selected_country)
    if selected_year=="Overall" and selected_country=="Overall":
        st.title("Overall Tally")
    if selected_year!="Overall" and selected_country=="Overall":
        st.title("Medal Tally in" +str(selected_year)+" Olympics")
    if selected_year=="Overall" and selected_country!="Overall":
        st.title(selected_country+"Overall Performance")
    if selected_year!="Overall" and selected_country!="Overall":
        st.title(selected_country+" performance in "+str(selected_year)+" Olympics")
    st.table(medal_tally)

if user_menu=="Overall Analysis":
    editions=df["Year"].unique().shape[0]-1
    cities=df["City"].unique().shape[0]
    sports=df["Sport"].unique().shape[0]
    events=df["Event"].unique().shape[0]
    athletes=df["Name"].unique().shape[0]
    nations=df["region"].unique().shape[0]

    st.title("Top Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Hosts")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Nations")
        st.title(nations)
    with col3:
        st.header("Athletes")
        st.title(athletes)

    nations_over_time=helper.participating_nations_over_time(df)
    fig = px.line(nations_over_time, x='Year', y='count',title='Number of Countries Participating in Summer Olympics Over Time', hover_data=['Year', 'count'])
    st.plotly_chart(fig)

    st.header("Events Over Time")

    events_over_time_df = helper.events_over_time(df)

    fig = px.line(
        events_over_time_df,
        x='Edition',
        y='No of Events',
        title='Number of Events in Summer Olympics Over Time',
        hover_data=['Edition', 'No of Events']
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------- ATHLETES OVER TIME ----------
    st.header("Athletes Over Time")

    athletes_over_time_df = helper.athletes_over_time(df)

    fig = px.line(
        athletes_over_time_df,
        x='Edition',
        y='No of Athletes',
        title='Number of Athletes in Summer Olympics Over Time',
        hover_data=['Edition', 'No of Athletes']
    )

    st.plotly_chart(fig, use_container_width=True)

    import seaborn as sns
    import matplotlib.pyplot as plt

    # ---------- SPORT vs YEAR HEATMAP ----------
    st.header("Sports Participation Over the Years")

    heatmap_df = helper.sport_year_heatmap(df)

    fig, ax = plt.subplots(figsize=(20, 20))
    sns.heatmap(
        heatmap_df,
        annot=True,
        fmt='d',
        cmap='coolwarm',
        ax=ax
    )

    st.pyplot(fig)
    # ---------- MOST SUCCESSFUL ATHLETES ----------
    st.header("Most Successful Athletes")

    # Sport selection
    sports_list = df["Sport"].dropna().unique().tolist()
    sports_list.sort()
    sports_list.insert(0, "Overall")

    selected_sport = st.selectbox("Select Sport", sports_list)

    top_athletes = helper.most_successfull(df, selected_sport)

    st.table(top_athletes)

if user_menu == "Country-wise analysis":
    st.header("Country-wise Analysis")

    # Country selection (ONLY ONCE)
    country_list = df["region"].dropna().unique().tolist()
    country_list.sort()

    selected_country = st.selectbox(
        "Select Country",
        country_list,
        key="country_analysis_selectbox"
    )

    # -------- MEDALS OVER TIME --------
    st.subheader(f"Medal Trend of {selected_country}")

    medals_per_year = helper.country_medals_over_time(df, selected_country)

    fig = px.line(
        medals_per_year,
        x='Year',
        y='Medal',
        title=f'Number of Medals for {selected_country} Over Time',
        hover_data=['Year', 'Medal']
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------- HEATMAP --------
    st.subheader(f"{selected_country} Performance Across Sports & Years")

    heatmap_df = helper.country_sport_heatmap(df, selected_country)

    if heatmap_df.empty:
        st.warning(f"No medal data available for {selected_country}.")
    else:
        import seaborn as sns
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(20, 20))
        sns.heatmap(
            heatmap_df,
            annot=True,
            fmt='g',
            cmap="YlOrRd",
            ax=ax
        )
        st.pyplot(fig)

    st.subheader(f"Most Successful Athletes from {selected_country}")
    top_athletes_country = helper.most_successful_by_country(df, selected_country)
    st.table(top_athletes_country)

if user_menu == "Athletes-wise analysis":
    st.header("Athletes Analysis")

    st.subheader("Age Distribution of Athletes")

    fig = helper.age_distribution(df)

    if fig is None:
        st.warning("No age data available for athletes.")
    else:
        st.plotly_chart(fig, use_container_width=True)

    st.header("Athletes-wise Analysis")

    st.subheader("Age Distribution of Gold Medalists (SciPy Distplot)")

    fig = helper.gold_medalist_age_dist_scipy(df)

    if fig is None:
        st.warning("No gold medal age data available for selected sports.")
    else:
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Height vs Weight Analysis by Sport")

    # Sport selectbox
    sport_list = df["Sport"].dropna().unique().tolist()
    sport_list.sort()

    selected_sport = st.selectbox(
        "Select Sport",
        sport_list,
        index=sport_list.index("Athletics") if "Athletics" in sport_list else 0
    )

    fig = helper.height_weight_scatter_by_sport(df, selected_sport)

    if fig is None:
        st.warning(f"No height/weight data available for {selected_sport}.")
    else:
        st.pyplot(fig)



