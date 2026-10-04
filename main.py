import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


# Load environment variables from .env
load_dotenv()


def get_database_engine():
    """Create a connection to PostgreSQL."""

    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")

    database_url = (
        f"postgresql+psycopg2://{user}:{password}"
        f"@{host}:{port}/{database}"
    )

    engine = create_engine(database_url)

    return engine


def extract_data():
    """Extract raw data from the CSV file."""

    df = pd.read_csv("data/raw/customer_churn.csv")

    print(f"Extracted {len(df)} rows")

    return df


def clean_and_transform(df):
    """Clean and transform the raw dataset."""

    # 1. Remove exact duplicate rows
    df = df.drop_duplicates()

    # 2. Check for missing values
    if df.isnull().sum().sum() > 0:
        raise ValueError("Dataset contains missing values")

    # 3. Convert Onboard_date from string to datetime
    df["Onboard_date"] = pd.to_datetime(df["Onboard_date"])

    # 4. Make sure Churn is an integer
    df["Churn"] = df["Churn"].astype(int)

    # 5. Validate Churn values
    if not df["Churn"].isin([0, 1]).all():
        raise ValueError("Churn must contain only 0 and 1")

    # 6. Validate Account_Manager values
    if not df["Account_Manager"].isin([0, 1]).all():
        raise ValueError("Account_Manager must contain only 0 and 1")

    return df


def load_data(df, engine):
    """Load cleaned data into PostgreSQL."""

    df.to_sql(
        "customer_churn",
        con=engine,
        if_exists="replace",
        index=False
    )

    print(f"Loaded {len(df)} rows into PostgreSQL")


def main():
    # --------------------------------------------------
    # DATABASE CONNECTION
    # --------------------------------------------------

    engine = get_database_engine()

    with engine.connect():
        print("Successfully connected to PostgreSQL!")

    # --------------------------------------------------
    # EXTRACT
    # --------------------------------------------------

    df = extract_data()

    print("\nBefore transformation:")
    print(df.dtypes)

    # --------------------------------------------------
    # TRANSFORM
    # --------------------------------------------------

    df = clean_and_transform(df)

    print("\nAfter transformation:")
    print(df.dtypes)

    print("\nFinal shape:")
    print(df.shape)

    print("\nFirst 5 rows:")
    print(df.head())

    # --------------------------------------------------
    # LOAD
    # --------------------------------------------------

    load_data(df, engine)


if __name__ == "__main__":
    main()