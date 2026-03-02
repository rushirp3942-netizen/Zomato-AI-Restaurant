import os
import json
from groq import Groq
from dotenv import load_dotenv
import sys

# Add parent directory to path to import Phase 2 engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from phase2_retrieval.retrieval_engine import RetrievalEngine

load_dotenv()

class RestaurantOrchestrator:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        # Use environment variable for DB path, fallback to local path
        db_path = os.getenv("DB_PATH")
        self.retrieval_engine = RetrievalEngine(db_path=db_path)
        self.model = "llama-3.3-70b-versatile"

    def extract_search_params(self, user_query):
        """
        Uses LLM to extract structured filters from a natural language query.
        """
        prompt = f"""
        Extract restaurant search parameters from the following user query:
        "{user_query}"
        
        Return ONLY a JSON object with these keys:
        - "cuisine" (string or null)
        - "location" (string or null)
        - "min_rating" (float, default 0.0)
        - "max_cost" (integer or null)
        
        Example Output: {{"cuisine": "Italian", "location": "Bangalore", "min_rating": 4.0, "max_cost": 1000}}
        """
        
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)

    def generate_recommendation(self, user_query, restaurants_df):
        """
        Uses LLM to generate structured Flash Card data for restaurants.
        """
        if restaurants_df.empty:
            return json.dumps({"recommendations": []})

        # Prepare a concise summary of the top 3-5 restaurants
        df = restaurants_df[['name', 'cuisines', 'location', 'rate', 'approx_cost(for two people)']].head(5).copy()
        df.columns = ['name', 'cuisines', 'location', 'rating', 'cost']
        context = df.to_dict(orient='records')
        
        prompt = f"""
        User Query: "{user_query}"
        
        Available Restaurant Data:
        {json.dumps(context)}
        
        Based on the user's request, select 3 UNIQUE and best matching restaurants from the list above. 
        It is critical that you do not repeat the same restaurant. Return a JSON object.
        For EACH restaurant, include:
        - "name": Restaurant name
        - "location": Locality
        - "rating": Numeric rating (e.g. 4.3)
        - "cuisines": Cuisine string
        - "cost": Numeric cost for two
        - "match_score": A percentage (0-100) based on how well it matches the user's cuisine, budget, and rating preferences.
        - "ai_summary": A one-line catchy summary of its key strength.
        - "why_this": 2 concise sentences explaining why it was recommended for this specific query.
        
        Return ONLY a JSON object with a "recommendations" key containing the list.
        """
        
        response = self.client.chat.completions.create(
            messages=[{"role": "system", "content": "You are a professional Restaurant Concierge in Bangalore. Return valid JSON."},
                      {"role": "user", "content": prompt}],
            model=self.model,
            response_format={"type": "json_object"}
        )
        
        return response.choices[0].message.content

    def generate_similar_recommendations(self, ref_restaurant, similar_df):
        """
        Uses LLM to generate recommendations similar to a reference restaurant.
        """
        if similar_df.empty:
            return json.dumps({"recommendations": []})

        # Prepare context
        df = similar_df[['name', 'cuisines', 'location', 'rate', 'approx_cost(for two people)']].head(5).copy()
        df.columns = ['name', 'cuisines', 'location', 'rating', 'cost']
        context = df.to_dict(orient='records')

        prompt = f"""
        Reference Restaurant: {json.dumps(ref_restaurant)}
        
        Find 3 UNIQUE restaurants from the following list that are most SIMILAR to the Reference Restaurant above.
        Ensure you do not return the same restaurant multiple times.
        List: {json.dumps(context)}
        
        Similarity factors:
        1. Cuisine overlap
        2. Price proximity
        3. Rating comparability
        4. Location neighborhood
        
        Return a JSON object. For EACH similar restaurant, include:
        - "name", "location", "rating", "cuisines", "cost"
        - "match_score": Percentage of similarity to the reference restaurant.
        - "ai_summary": One-liner highlighting the similarity (e.g., "Same great North Indian taste").
        - "why_this": 2 sentences explaining the similarity factor (e.g., "Like {ref_restaurant['name']}, this place offers premium Mughlai at a mid-range price.").
        
        Return ONLY a JSON object with a "recommendations" key.
        """

        response = self.client.chat.completions.create(
            messages=[{"role": "system", "content": "You are a professional Restaurant Concierge. Identify similarities accurately. Return valid JSON."},
                      {"role": "user", "content": prompt}],
            model=self.model,
            response_format={"type": "json_object"}
        )
        
        return response.choices[0].message.content

    def chat(self, user_query):
        """
        Complete flow: Query -> Parse -> Retrieve -> Recommend
        """
        print(f"\n--- Processing: '{user_query}' ---")
        
        # 1. Extract params
        print("1. Extracting parameters...")
        params = self.extract_search_params(user_query)
        print(f"   Searching for: {params}")
        
        # 2. Query DB
        print("2. Querying database...")
        results = self.retrieval_engine.query_restaurants(
            cuisine=params.get("cuisine"),
            location=params.get("location"),
            min_rating=params.get("min_rating", 0.0),
            max_cost=params.get("max_cost")
        )
        print(f"   Found {len(results)} matches.")
        
        # 3. Generate Final Response
        print("3. Generating AI recommendation...")
        recommendation = self.generate_recommendation(user_query, results)
        
        return recommendation

if __name__ == "__main__":
    orchestrator = RestaurantOrchestrator()
    
    # Test queries
    test_queries = [
        "I want a cheap Italian place in Bangalore with at least a 4 star rating",
        "Suggest some premium North Indian dining spots in Indiranagar"
    ]
    
    for query in test_queries:
        response = orchestrator.chat(query)
        print("\nAI Response:")
        try:
            print(response)
        except UnicodeEncodeError:
            print(response.encode('utf-8').decode('ascii', 'ignore'))
        print("-" * 50)
