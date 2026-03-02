import os
import sys
import unittest

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from phase5_evaluation.evaluator import SystemEvaluator

class TestEvaluationPhase(unittest.TestCase):
    def setUp(self):
        self.evaluator = SystemEvaluator()

    def test_evaluator_initialization(self):
        """Test if golden queries are correctly loaded."""
        self.assertGreater(len(self.evaluator.golden_queries), 0)
        self.assertEqual(self.evaluator.golden_queries[0]['expected_constraints']['cuisine'], "Italian")

    def test_relevance_scoring_logic(self):
        """Test if the LLM-as-a-judge returns a valid score."""
        query = "Show me good pizza"
        recommendation = "I recommend Joe's Pizza because it has a 4.5 rating and serves authentic Italian pizza."
        score = self.evaluator.evaluate_relevance_with_llm(query, recommendation)
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 10)

if __name__ == "__main__":
    unittest.main()
