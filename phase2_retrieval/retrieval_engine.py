import sqlite3
import pandas as pd
import os

class RetrievalEngine:
    def __init__(self, db_path=None):
        # Use environment variable or default to local path for Streamlit Cloud
        if db_path is None:
            db_path = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "restaurants.db"))
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def query_restaurants(self, cuisine=None, location=None, min_rating=0.0, max_cost=None):
        """
        Retrieves restaurants based on filters.
        """
        query = "SELECT * FROM restaurants WHERE rate >= ?"
        params = [min_rating]

        if cuisine:
            query += " AND cuisines LIKE ?"
            params.append(f"%{cuisine}%")
        
        if location and location.lower() != "bangalore":
            query += " AND (location LIKE ? OR \"listed_in(city)\" LIKE ?)"
            params.append(f"%{location}%")
            params.append(f"%{location}%")
            
        if max_cost:
            # Assuming 'approx_cost_for_two_people' is the column name
            query += " AND \"approx_cost(for two people)\" <= ?"
            params.append(max_cost)

        query += " ORDER BY rate DESC LIMIT 100"

        conn = self.get_connection()
        try:
            results = pd.read_sql_query(query, conn, params=params)
            # Deduplicate by restaurant name
            results = results.drop_duplicates(subset='name').head(10)
            return results
        finally:
            conn.close()

if __name__ == "__main__":
    # Quick manual test
    engine = RetrievalEngine("D:/restaurants.db")
    try:
        print("Testing retrieval engine...")
        res = engine.query_restaurants(cuisine="Italian", location="Bangalore", min_rating=4.0)
        print("\nResults:")
        try:
            print(res.head())
        except UnicodeEncodeError:
            print(str(res.head()).encode('utf-8').decode('ascii', 'ignore'))
        print("-" * 50)
    except Exception as e:
        print(f"Note: Could not run retrieval test: {e}")
