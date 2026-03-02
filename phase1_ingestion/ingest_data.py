import pandas as pd
import sqlite3
import os
from datasets import load_dataset

# Configuration - use environment variable or default to local path
DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "restaurants.db"))
HF_CACHE = os.getenv("HF_CACHE", os.path.join(os.path.dirname(__file__), "..", "hf_cache"))

def download_and_clean_data(dataset_name="ManikaSaini/zomato-restaurant-recommendation"):
    """
    Downloads the dataset from Hugging Face and cleans common Zomato data issues.
    """
    print(f"Loading dataset from Hugging Face: {dataset_name}...")
    try:
        # Load dataset as pandas dataframe with cache on D:
        dataset = load_dataset(dataset_name, cache_dir=HF_CACHE)
        df = dataset['train'].to_pandas()
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None

    print("Cleaning data...")
    
    # 1. Handle Ratings (convert string to float, e.g., '4.1/5' -> 4.1)
    if 'rate' in df.columns:
        def clean_rate(x):
            if pd.isna(x):
                return None
            x = str(x)
            if '/' in x:
                return x.split('/')[0]
            return x
        
        df['rate'] = df['rate'].apply(clean_rate)
        df['rate'] = pd.to_numeric(df['rate'], errors='coerce')
    
    # 2. Handle Approx Cost (remove commas, convert to numeric)
    cost_cols = [c for c in df.columns if 'cost' in c.lower()]
    for col in cost_cols:
        df[col] = df[col].astype(str).str.replace(',', '').str.replace(' ', '')
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 3. Fill missing values
    df['cuisines'] = df['cuisines'].fillna('Other')
    df['location'] = df['location'].fillna('Unknown')
    df['dish_liked'] = df['dish_liked'].fillna('')
    
    # 4. Drop duplicates
    df = df.drop_duplicates()

    return df

def save_to_sqlite(df, db_path=DB_PATH):
    """
    Saves the cleaned dataframe to a SQLite database for Phase 2 retrieval.
    """
    if df is None:
        return
    
    print(f"Saving {len(df)} records to {db_path}...")
    conn = sqlite3.connect(db_path)
    df.to_sql('restaurants', conn, if_exists='replace', index=False)
    conn.close()
    print("Data ingestion complete.")

if __name__ == "__main__":
    data = download_and_clean_data()
    if data is not None:
        save_to_sqlite(data)
