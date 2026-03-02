from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys

# Add root directory to sys.path to import modules from other phases
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)
from phase3_llm.llm_service import RestaurantOrchestrator

app = FastAPI(
    title="AI Restaurant Recommendation API",
    description="REST API for personalized restaurant recommendations using Groq LLM and Zomato data.",
    version="1.0.0"
)

# Initialize Orchestrator
orchestrator = RestaurantOrchestrator()

# Mount Static Files
app.mount("/static", StaticFiles(directory=os.path.join(PROJECT_ROOT, "frontend")), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(PROJECT_ROOT, "frontend", "index.html"))

class RecommendationRequest(BaseModel):
    query: str

class SimilarRequest(BaseModel):
    name: str
    cuisines: str
    location: str
    rating: float
    cost: int

class RecommendationResponse(BaseModel):
    query: str
    recommendation: str

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "D:/restaurants.db"}

@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendation(request: RecommendationRequest):
    """
    Accepts a natural language query and returns an AI-generated restaurant recommendation.
    """
    try:
        # The orchestrator.chat method handles the full flow: Parse -> Retrieve -> Recommend
        ai_response = orchestrator.chat(request.query)
        return RecommendationResponse(
            query=request.query,
            recommendation=ai_response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/similar", response_model=RecommendationResponse)
async def get_similar_recommendation(request: SimilarRequest):
    """
    Finds restaurants similar to the one provided in the request.
    """
    try:
        # 1. Fetch candidates from DB based on reference attributes
        # We'll search for same cuisine/location to find "similar" ones
        primary_cuisine = request.cuisines.split(',')[0].strip()
        candidates = orchestrator.retrieval_engine.query_restaurants(
            cuisine=primary_cuisine,
            location=request.location,
            min_rating=max(0.0, request.rating - 0.5),
            max_cost=int(request.cost * 1.5)
        )
        
        # 2. Filter out the original restaurant if present
        candidates = candidates[candidates['name'] != request.name]
        
        # 3. Generate AI Re-ranking/Reasoning
        ai_response = orchestrator.generate_similar_recommendations(request.dict(), candidates)
        
        return RecommendationResponse(
            query=f"Similar to {request.name}",
            recommendation=ai_response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
