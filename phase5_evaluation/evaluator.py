import os
import json
import time
import sys
import pandas as pd
from typing import List, Dict

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from phase3_llm.llm_service import RestaurantOrchestrator

class SystemEvaluator:
    def __init__(self):
        self.orchestrator = RestaurantOrchestrator()
        self.golden_queries = [
            {
                "query": "I want a cheap Italian place in Bangalore with at least 4 star rating",
                "expected_constraints": {"cuisine": "Italian", "min_rating": 4.0}
            },
            {
                "query": "Suggest some premium North Indian dining spots in Indiranagar",
                "expected_constraints": {"cuisine": "North Indian", "location": "Indiranagar", "min_rating": 4.0}
            },
            {
                "query": "Best Chinese food under 500 rupees in Koramangala",
                "expected_constraints": {"cuisine": "Chinese", "location": "Koramangala", "max_cost": 500}
            }
        ]

    def evaluate_relevance_with_llm(self, query: str, recommendation: str) -> int:
        """
        Uses the LLM as a judge to score the recommendation relevance.
        """
        prompt = f"""
        User Query: "{query}"
        AI Recommendation: "{recommendation}"
        
        On a scale of 1-10, how well does the AI recommendation address the user's query?
        Consider:
        - Did it find restaurants matching the requested cuisine?
        - Did it respect the location/price constraints?
        - Is the tone helpful?
        
        Return ONLY the integer score.
        """
        try:
            response = self.orchestrator.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.orchestrator.model
            )
            score_str = response.choices[0].message.content.strip()
            # Extract digits only in case LLM adds text
            score = int(''.join(filter(str.isdigit, score_str)))
            return score
        except:
            return 0

    def run_evaluation(self):
        print("Starting System Evaluation Phase 5...")
        results = []
        
        for item in self.golden_queries:
            query = item["query"]
            print(f"\nEvaluating Query: '{query}'")
            
            start_time = time.time()
            # Run the actual orchestrator flow
            # Note: Orchestrator.chat prints a lot, which is fine for visibility
            recommendation = self.orchestrator.chat(query)
            latency = time.time() - start_time
            
            # LLM-as-a-judge score
            relevance_score = self.evaluate_relevance_with_llm(query, recommendation)
            
            result = {
                "query": query,
                "latency_sec": round(latency, 2),
                "relevance_score": relevance_score,
                "recommendation_length": len(recommendation)
            }
            results.append(result)
            print(f"  Latency: {result['latency_sec']}s")
            print(f"  Relevance Score (LLM-as-judge): {result['relevance_score']}/10")

        # Generate Report
        df = pd.DataFrame(results)
        report_path = os.path.join(os.path.dirname(__file__), "evaluation_report.csv")
        df.to_csv(report_path, index=False)
        
        print(f"\nEvaluation Complete. Report saved to {report_path}")
        print("\nSummary Metrics:")
        print(f"  Average Latency: {df['latency_sec'].mean():.2f}s")
        print(f"  Average Relevance Score: {df['relevance_score'].mean():.1f}/10")

if __name__ == "__main__":
    evaluator = SystemEvaluator()
    evaluator.run_evaluation()
