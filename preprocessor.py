import pandas as pd

def preprocess(df, region_df):
    # Filter Summer Olympics
    df = df[df["Season"] == "Summer"].copy()

    # Merge NOC with region (safe)
    df = df.merge(region_df, on="NOC", how="left")

    # Remove duplicate rows
    df.drop_duplicates(inplace=True)

    # Create Medal columns safely
    df["Gold"] = (df["Medal"] == "Gold").astype(int)
    df["Silver"] = (df["Medal"] == "Silver").astype(int)
    df["Bronze"] = (df["Medal"] == "Bronze").astype(int)

    return df

