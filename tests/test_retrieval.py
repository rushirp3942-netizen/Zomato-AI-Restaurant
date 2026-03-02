import unittest
import pandas as pd
import sqlite3
import os
import sys

# Add parent directories to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phase2_retrieval.retrieval_engine import RetrievalEngine

class TestRetrievalEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a mock database for testing
        cls.db_path = "test_restaurants.db"
        conn = sqlite3.connect(cls.db_path)
        data = {
            'name': ['Pasta Place', 'Burger Joint', 'Sushi Zen'],
            'cuisines': ['Italian', 'American, Fast Food', 'Japanese'],
            'location': ['Bangalore', 'Bangalore', 'Delhi'],
            'rate': [4.5, 3.8, 4.2],
            'approx_cost(for two people)': [800, 400, 1500]
        }
        df = pd.DataFrame(data)
        df.to_sql('restaurants', conn, index=False)
        conn.close()
        cls.engine = RetrievalEngine(cls.db_path)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def test_cuisine_filter(self):
        results = self.engine.query_restaurants(cuisine="Italian")
        self.assertEqual(len(results), 1)
        self.assertEqual(results.iloc[0]['name'], 'Pasta Place')

    def test_rating_filter(self):
        results = self.engine.query_restaurants(min_rating=4.0)
        self.assertEqual(len(results), 2)
        self.assertTrue(all(results['rate'] >= 4.0))

    def test_cost_filter(self):
        results = self.engine.query_restaurants(max_cost=500)
        self.assertEqual(len(results), 1)
        self.assertEqual(results.iloc[0]['name'], 'Burger Joint')

if __name__ == '__main__':
    unittest.main()
