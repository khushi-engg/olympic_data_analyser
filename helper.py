import numpy as np
def fetch_medal_tally(df, year, country):
    medal_df = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    flag = 0
    if year == 'Overall' and country == 'Overall':
        temp_df = medal_df
    if year == 'Overall' and country != 'Overall':
        flag = 1
        temp_df = medal_df[medal_df['region'] == country]
    if year != 'Overall' and country == 'Overall':
        temp_df = medal_df[medal_df['Year'] == int(year)]
    if year != 'Overall' and country != 'Overall':
        temp_df = medal_df[(medal_df['Year'] == year) & (medal_df['region'] == country)]

    if flag == 1:
        x = temp_df.groupby('Year').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Year').reset_index()
    else:
        x = temp_df.groupby('region').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold',
                                                                                      ascending=False).reset_index()

    x['total'] = x['Gold'] + x['Silver'] + x['Bronze']

    x['Gold'] = x['Gold'].astype('int')
    x['Silver'] = x['Silver'].astype('int')
    x['Bronze'] = x['Bronze'].astype('int')
    x['total'] = x['total'].astype('int')

    return x

def country_year_list(df):
    Years = df["Year"].unique().tolist()
    Years.sort()
    Years.insert(0, "Overall")

    country=np.unique(df["region"].dropna().values).tolist()
    country.sort()
    country.insert(0, "Overall")

    return Years,country
def participating_nations_over_time(df):
    # Remove duplicate country participation per year
    temp_df = df.drop_duplicates(subset=['Year', 'region'])

    # Count participating nations per year
    nations_over_time = temp_df.groupby('Year')['region'] \
                                .count() \
                                .reset_index()

    nations_over_time.rename(columns={'region': 'count'}, inplace=True)

    return nations_over_time
def events_over_time(df):
    # Remove duplicate events per year
    temp_df = df.drop_duplicates(subset=['Year', 'Event'])

    # Count number of events per year
    events_df = temp_df.groupby('Year')['Event'] \
                        .count() \
                        .reset_index()

    # Rename columns clearly
    events_df.rename(
        columns={
            'Year': 'Edition',
            'Event': 'No of Events'
        },
        inplace=True
    )

    return events_df
def athletes_over_time(df):
    # Each athlete counted once per Olympic edition
    temp_df = df.drop_duplicates(subset=['Year', 'Name'])

    # Count athletes per year
    athletes_df = temp_df.groupby('Year')['Name'] \
                          .count() \
                          .reset_index()

    # Rename columns for clarity
    athletes_df.rename(
        columns={
            'Year': 'Edition',
            'Name': 'No of Athletes'
        },
        inplace=True
    )

    return athletes_df
def sport_year_heatmap(df):
    # Remove duplicate events to avoid double counting
    temp_df = df.drop_duplicates(subset=['Year', 'Sport', 'Event'])

    # Create pivot table
    heatmap_df = temp_df.pivot_table(
        index='Sport',
        columns='Year',
        values='Event',
        aggfunc='count'
    ).fillna(0).astype(int)

    return heatmap_df
def most_successfull(df, sport):
    temp_df = df.dropna(subset=["Medal"])

    if sport != "Overall":
        temp_df = temp_df[temp_df["Sport"] == sport]

    # Count medals per athlete
    athlete_medal_counts = temp_df["Name"].value_counts().reset_index()
    athlete_medal_counts.columns = ["Name", "Medals"]

    # Merge to get Sport and region
    merged_data = athlete_medal_counts.merge(
        df,
        on="Name",
        how="left"
    )

    # Select relevant columns and remove duplicates
    final_df = merged_data[
        ["Name", "Medals", "Sport", "region"]
    ].drop_duplicates(subset=["Name"])

    # Sort by medals (descending) and take top 15
    final_df = final_df.sort_values("Medals", ascending=False).head(15)

    return final_df.rename(columns={"Name": "Athlete Name"})


def country_medals_over_time(df, country):
    # Remove rows without medals
    temp_df = df.dropna(subset=["Medal"])

    # Filter by country
    temp_df = temp_df[temp_df["region"] == country]

    # Count medals per year
    medals_over_time = temp_df.groupby("Year")["Medal"] \
                              .count() \
                              .reset_index()

    return medals_over_time
def country_sport_heatmap(df, country):
    temp_df = df.dropna(subset=["Medal"])
    temp_df = temp_df[temp_df["region"] == country]

    temp_df = temp_df.drop_duplicates(["Sport", "Year", "Event"])

    heatmap_df = temp_df.pivot_table(
        index="Sport",
        columns="Year",
        values="Medal",
        aggfunc="count"
    ).fillna(0)

    return heatmap_df

import pandas as pd
def most_successful_by_country(df, country):

    # Remove rows without medals
    temp_df = df.dropna(subset=["Medal"])

    # Filter by country
    temp_df = temp_df[temp_df["region"] == country]

    if temp_df.empty:
        # No medals for this country
        return pd.DataFrame(columns=["Athlete Name", "Medals", "Sport", "region"])

    # Count medals per athlete
    athlete_medal_counts = temp_df["Name"].value_counts().reset_index()
    athlete_medal_counts.columns = ["Name", "Medals"]

    # Merge to get Sport and region
    merged_data = athlete_medal_counts.merge(
        df[["Name", "Sport", "region"]].drop_duplicates(subset=["Name"]),
        on="Name",
        how="left"
    )

    # Sort by medal count descending
    merged_data = merged_data.sort_values("Medals", ascending=False).head(15)

    # Rename column for display
    merged_data = merged_data.rename(columns={"Name": "Athlete Name"})

    return merged_data

import plotly.figure_factory as ff

def age_distribution(df):
    """
    Returns a Plotly distplot figure of athlete ages.
    Includes Overall, Gold, Silver, and Bronze medalists.
    """
    # Remove duplicate athletes to avoid double-counting
    athlete_df = df.drop_duplicates(subset=["Name", "region"])

    # Overall age distribution
    overall_age = athlete_df["Age"].dropna()

    # Age distributions by medal
    gold_age = athlete_df[athlete_df["Medal"] == "Gold"]["Age"].dropna()
    silver_age = athlete_df[athlete_df["Medal"] == "Silver"]["Age"].dropna()
    bronze_age = athlete_df[athlete_df["Medal"] == "Bronze"]["Age"].dropna()

    # If all distributions are empty, return None
    if overall_age.empty and gold_age.empty and silver_age.empty and bronze_age.empty:
        return None

    # Create distplot
    fig = ff.create_distplot(
        [overall_age, gold_age, silver_age, bronze_age],
        ["Overall Age", "Gold Medalist", "Silver Medalist", "Bronze Medalist"],
        show_hist=False,
        show_rug=False
    )

    fig.update_layout(
        title_text="Age Distribution of Athletes",
        xaxis_title="Age",
        yaxis_title="Density",
        template="plotly_white"
    )

    return fig
import pandas as pd
import plotly.express as px

import plotly.figure_factory as ff
import pandas as pd

def gold_medalist_age_dist_scipy(df):
    """
    Returns a SciPy-based distplot for age distribution
    of gold medalists across famous sports
    """

    famous_sports = [
        'Basketball', 'Judo', 'Football', 'Tug-Of-War', 'Athletics',
        'Swimming', 'Badminton', 'Sailing', 'Gymnastics',
        'Art Competitions', 'Handball', 'Weightlifting', 'Wrestling',
        'Water Polo', 'Hockey', 'Rowing', 'Fencing',
        'Shooting', 'Boxing', 'Taekwondo', 'Cycling', 'Diving',
        'Canoeing', 'Tennis', 'Golf', 'Softball', 'Archery',
        'Volleyball', 'Synchronized Swimming', 'Table Tennis',
        'Baseball', 'Rhythmic Gymnastics', 'Rugby Sevens',
        'Beach Volleyball', 'Triathlon', 'Rugby', 'Polo', 'Ice Hockey'
    ]

    athlete_df = df.drop_duplicates(subset=["Name", "region"])

    x = []
    labels = []

    for sport in famous_sports:
        ages = athlete_df[
            (athlete_df["Sport"] == sport) &
            (athlete_df["Medal"] == "Gold")
        ]["Age"].dropna()

        if not ages.empty:
            x.append(ages)
            labels.append(sport)

    # VERY IMPORTANT: avoid empty plot
    if len(x) == 0:
        return None

    fig = ff.create_distplot(
        x,
        labels,
        show_hist=False,
        show_rug=False
    )

    fig.update_layout(
        title="Age Distribution of Gold Medalists Across Sports (SciPy)",
        xaxis_title="Age",
        yaxis_title="Density",
        template="plotly_white"
    )

    return fig
import seaborn as sns
import matplotlib.pyplot as plt

def height_weight_scatter_by_sport(df, sport):
    """
    Returns a Height vs Weight scatter plot for a selected sport,
    colored by Medal and styled by Sex.
    """

    athlete_df = df.drop_duplicates(subset=["Name", "region"])

    temp_df = athlete_df[
        (athlete_df["Sport"] == sport) &
        (athlete_df["Height"].notna()) &
        (athlete_df["Weight"].notna())
    ]

    if temp_df.empty:
        return None

    fig, ax = plt.subplots(figsize=(10, 10))

    sns.scatterplot(
        data=temp_df,
        x="Weight",
        y="Height",
        hue="Medal",
        style="Sex",
        s=100,
        ax=ax
    )

    ax.set_title(f"Height vs Weight of {sport} Athletes")
    ax.set_xlabel("Weight (kg)")
    ax.set_ylabel("Height (cm)")

    return fig





