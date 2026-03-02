# AI Restaurant Recommendation Service

An AI-powered service that provides personalized restaurant recommendations using the Zomato Bangalore dataset (51k+ records) and Groq LLMs.

## 🚀 Quick Start (Running Locally)

The project is already set up on the **D: Drive** at `D:\Python312` and uses a virtual environment at `D:\venv`.

### 1. Start the API Server
Open a terminal and run:
```powershell
D:\venv\Scripts\python.exe phase4_api/api_service.py
```
*The server runs on `http://127.0.0.1:8000`.*

### 2. Test the API
You can run the pre-built integration test:
```powershell
D:\venv\Scripts\python.exe tests/test_api.py
```

Or use **PowerShell** to send a manual query:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/recommend" -Method Post -ContentType "application/json" -Body '{"query": "I want a high-rated Chinese restaurant in Bangalore under 1000 rupees"}' | Select-Object -ExpandProperty recommendation
```

## 📂 Project Structure

- **phase1_ingestion/**: Data download (from Hugging Face) and cleaning logic.
- **phase2_retrieval/**: SQLite-based search engine with smart location matching.
- **phase3_llm/**: Groq Llama 3 Orchestrator for query parsing and response generation.
- **phase4_api/**: FastAPI REST service with `/recommend` and `/health` endpoints.
- **phase5_evaluation/**: Performance metrics suite (Latency & Relevance).
- **tests/**: Automated unit and integration tests.

## 📊 Evaluation Results
- **Average Latency**: ~2.9s
- **Accuracy (LLM-as-judge)**: 7.7/10

## 🔧 Environment Variables
Ensure your `.env` file in the root directory contains your Groq API Key:
```env
GROQ_API_KEY=your_key_here
```

## 🛠️ Components Used
- **LLM**: Groq (Llama-3.3-70b-versatile)
- **Framework**: FastAPI, Pydantic, Pandas, Datasets
- **Database**: SQLite (Stored at `D:/restaurants.db`)
