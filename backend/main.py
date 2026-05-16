import json
import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date as DateType
from typing import List

from backend.aggregator import fetch_articles
from backend.summarizer import summarize_articles
from backend.preferences import load_preferences, save_preferences

app = FastAPI(title="Daily News Brief API")

# Allow Streamlit frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request/Response models ──────────────────────────────────────────────────

class PreferencesRequest(BaseModel):
    categories: List[str]
    language: str = "en"
    reading_style: str = "short"  # "short" or "detailed"

class BriefRequest(BaseModel):
    categories: List[str]
    date: str  # "YYYY-MM-DD"
    reading_style: str = "short"
HISTORY_FILE = "backend/brief_history.json"

def save_brief_to_history(date: str, data: dict):
    history = {}
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    history[date] = {
        "saved_at": datetime.now().isoformat(),
        "categories": list(data.get("categories", {}).keys()),
        "data": data
    }
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def load_history() -> dict:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}
# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Daily News Brief API is running"}

@app.get("/preferences")
def get_preferences():
    return load_preferences()

@app.post("/preferences")
def update_preferences(req: PreferencesRequest):
    prefs = {
        "categories": req.categories,
        "language": req.language,
        "reading_style": req.reading_style,
    }
    save_preferences(prefs)
    return {"status": "saved", "preferences": prefs}

@app.post("/brief")
def get_brief(req: BriefRequest):
    result = {}
    for category in req.categories:
        try:
            print(f"Processing {category}...")
            articles = fetch_articles(category, req.date)
            ai_output = summarize_articles(articles, category, req.reading_style)
            result[category] = {
                "articles": articles,
                "summaries": ai_output["summaries"],
                "brief": ai_output["brief"],
            }
            print(f"Done: {category}")
        except Exception as e:
            print(f"Error in {category}: {e}")
            result[category] = {
                "articles": [],
                "summaries": [],
                "brief": f"Could not load {category} news. Please try again.",
            }
    response_data = {
        "date": req.date,
        "categories": result,
    }
    save_brief_to_history(req.date, response_data)
    return response_data

@app.get("/brief/today")
def get_today_brief():
    prefs = load_preferences()
    today = str(DateType.today())
    result = {}
    for category in prefs["categories"]:
        articles = fetch_articles(category, today)
        ai_output = summarize_articles(articles, category, prefs["reading_style"])
        result[category] = {
            "articles": articles,
            "summaries": ai_output["summaries"],
            "brief": ai_output["brief"],
        }
    return {
        "date": today,
        "categories": result,
        "preferences": prefs,
    }
@app.get("/history")
def get_history():
    history = load_history()
    # Return just the dates and categories, not full data
    summary = {}
    for date, entry in history.items():
        summary[date] = {
            "saved_at": entry.get("saved_at", ""),
            "categories": entry.get("categories", [])
        }
    return {"history": summary}

@app.get("/history/{date}")
def get_brief_by_date(date: str):
    history = load_history()
    if date in history:
        return history[date]["data"]
    return {"error": f"No brief found for {date}"}