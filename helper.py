import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import seaborn as sns
import matplotlib.pyplot as plt

# ---------------- MEDAL TALLY ----------------
def fetch_medal_tally(df, year, country):

    medal_df = df.drop_duplicates(
        subset=['Team','NOC','Games','Year','City','Sport','Event','Medal']
    )

    flag = 0

    if year == "Overall" and country == "Overall":
        temp_df = medal_df

    elif year == "Overall" and country != "Overall":
        flag = 1
        temp_df = medal_df[medal_df["region"] == country]

    elif year != "Overall" and country == "Overall":
        temp_df = medal_df[medal_df["Year"] == int(year)]

    else:
        temp_df = medal_df[
            (medal_df["Year"] == int(year)) &
            (medal_df["region"] == country)
        ]

    if flag == 1:
        x = (
            temp_df
            .groupby("Year")[["Gold","Silver","Bronze"]]
            .sum()
            .sort_index()
            .reset_index()
        )
    else:
        x = (
            temp_df
            .groupby("region")[["Gold","Silver","Bronze"]]
            .sum()
            .sort_values("Gold", ascending=False)
            .reset_index()
        )

    x["total"] = x["Gold"] + x["Silver"] + x["Bronze"]

    return x.astype({
        "Gold": int,
        "Silver": int,
        "Bronze": int,
        "total": int
    })

# ---------------- DROPDOWNS ----------------
def country_year_list(df):
    years = sorted(df["Year"].unique().tolist())
    years.insert(0, "Overall")

    country = sorted(df["region"].dropna().unique().tolist())
    country.insert(0, "Overall")

    return years, country

# ---------------- OVERALL ANALYSIS ----------------
def participating_nations_over_time(df):
    temp_df = df.drop_duplicates(subset=["Year","region"])
    return (
        temp_df.groupby("Year")["region"]
        .count()
        .reset_index(name="count")
    )

def events_over_time(df):
    temp_df = df.drop_duplicates(subset=["Year","Event"])
    return (
        temp_df.groupby("Year")["Event"]
        .count()
        .reset_index(name="No of Events")
        .rename(columns={"Year":"Edition"})
    )

def athletes_over_time(df):
    temp_df = df.drop_duplicates(subset=["Year","Name"])
    return (
        temp_df.groupby("Year")["Name"]
        .count()
        .reset_index(name="No of Athletes")
        .rename(columns={"Year":"Edition"})
    )

def sport_year_heatmap(df):
    temp_df = df.drop_duplicates(subset=["Year","Sport","Event"])
    return (
        temp_df.pivot_table(
            index="Sport",
            columns="Year",
            values="Event",
            aggfunc="count"
        )
        .fillna(0)
        .astype(int)
    )

# ---------------- ATHLETES ----------------
def most_successfull(df, sport):
    temp_df = df.dropna(subset=["Medal"])

    if sport != "Overall":
        temp_df = temp_df[temp_df["Sport"] == sport]

    medals = temp_df["Name"].value_counts().reset_index()
    medals.columns = ["Athlete Name","Medals"]

    merged = medals.merge(
        df[["Name","Sport","region"]].drop_duplicates("Name"),
        left_on="Athlete Name",
        right_on="Name",
        how="left"
    )

    return (
        merged[["Athlete Name","Medals","Sport","region"]]
        .drop_duplicates("Athlete Name")
        .head(15)
    )

def country_medals_over_time(df, country):
    temp_df = df.dropna(subset=["Medal"])
    temp_df = temp_df[temp_df["region"] == country]

    return (
        temp_df.groupby("Year")["Medal"]
        .count()
        .reset_index()
    )

def country_sport_heatmap(df, country):
    temp_df = df.dropna(subset=["Medal"])
    temp_df = temp_df[temp_df["region"] == country]
    temp_df = temp_df.drop_duplicates(["Sport","Year","Event"])

    return (
        temp_df.pivot_table(
            index="Sport",
            columns="Year",
            values="Medal",
            aggfunc="count"
        )
        .fillna(0)
    )

def most_successful_by_country(df, country):
    temp_df = df.dropna(subset=["Medal"])
    temp_df = temp_df[temp_df["region"] == country]

    if temp_df.empty:
        return pd.DataFrame(
            columns=["Athlete Name","Medals","Sport","region"]
        )

    medals = temp_df["Name"].value_counts().reset_index()
    medals.columns = ["Athlete Name","Medals"]

    return (
        medals.merge(
            df[["Name","Sport","region"]].drop_duplicates("Name"),
            left_on="Athlete Name",
            right_on="Name",
            how="left"
        )
        .head(15)
    )

# ---------------- DISTRIBUTIONS ----------------
def age_distribution(df):
    athlete_df = df.drop_duplicates(subset=["Name","region"])

    overall = athlete_df["Age"].dropna()
    gold = athlete_df[athlete_df["Medal"]=="Gold"]["Age"].dropna()
    silver = athlete_df[athlete_df["Medal"]=="Silver"]["Age"].dropna()
    bronze = athlete_df[athlete_df["Medal"]=="Bronze"]["Age"].dropna()

    if all(x.empty for x in [overall,gold,silver,bronze]):
        return None

    fig = ff.create_distplot(
        [overall,gold,silver,bronze],
        ["Overall","Gold","Silver","Bronze"],
        show_hist=False,
        show_rug=False
    )
    return fig

def gold_medalist_age_dist_scipy(df):
    famous_sports = [
        'Basketball','Judo','Football','Athletics','Swimming',
        'Gymnastics','Hockey','Rowing','Boxing','Wrestling'
    ]

    athlete_df = df.drop_duplicates(subset=["Name","region"])

    x, labels = [], []
    for sport in famous_sports:
        ages = athlete_df[
            (athlete_df["Sport"] == sport) &
            (athlete_df["Medal"] == "Gold")
        ]["Age"].dropna()

        if not ages.empty:
            x.append(ages)
            labels.append(sport)

    if not x:
        return None

    return ff.create_distplot(x, labels, show_hist=False, show_rug=False)

def height_weight_scatter_by_sport(df, sport):
    athlete_df = df.drop_duplicates(subset=["Name","region"])

    temp_df = athlete_df[
        (athlete_df["Sport"] == sport) &
        athlete_df["Height"].notna() &
        athlete_df["Weight"].notna()
    ]

    if temp_df.empty:
        return None

    fig, ax = plt.subplots(figsize=(10,10))
    sns.scatterplot(
        data=temp_df,
        x="Weight",
        y="Height",
        hue="Medal",
        style="Sex",
        ax=ax
    )

    return fig



