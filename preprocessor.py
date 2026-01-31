import pandas as pd

def preprocess(df, region_df):
    # Filter Summer Olympics
    df = df[df["Season"] == "Summer"]

    # Merge only once
    if 'region' not in df.columns:
        df = df.merge(region_df, on="NOC", how="left")

    # Remove duplicates
    df = df.drop_duplicates()

    # One-hot encode medals
    medal_dummies = pd.get_dummies(df["Medal"])
    df = pd.concat([df, medal_dummies], axis=1)

    return df
