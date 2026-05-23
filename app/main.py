from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from app.agent import simulate_review, get_recommendations
from app.data import get_all_users, get_user_by_id, get_rating_pattern

load_dotenv()

app = FastAPI(
    title="Naija Agent — DSN x BCT Hackathon 3.0",
    description="LLM-powered User Modelling and Recommendation System with Nigerian context",
    version="1.0.0"
)

# ─── Request Models ───────────────────────────────────────────────────────────

class ReviewRequest(BaseModel):
    user_id: str
    item_name: str
    item_category: str
    item_description: str

class RecommendRequest(BaseModel):
    user_id: str
    category: str
    context: Optional[str] = ""
    conversation_history: Optional[List[dict]] = []

# ─── Pages ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def home():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

# ─── Data Endpoints ───────────────────────────────────────────────────────────

@app.get("/users")
def list_users():
    """Return all available user profiles across all three datasets"""
    users = get_all_users()
    return {
        "users": [
            {
                "user_id": u["user_id"],
                "name": u["name"],
                "location": u["location"],
                "profile": u["profile"],
                "yelp_reviews": len(u["yelp_reviews"]),
                "amazon_reviews": len(u["amazon_reviews"]),
                "goodreads_reviews": len(u["goodreads_reviews"]),
                "total_reviews": len(u["yelp_reviews"]) + len(u["amazon_reviews"]) + len(u["goodreads_reviews"])
            }
            for u in users
        ],
        "total": len(users)
    }

@app.get("/users/{user_id}")
def get_user(user_id: str):
    """Return full profile and review history for a specific user"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    pattern = get_rating_pattern(user_id)
    
    return {
        "user": user,
        "rating_pattern": pattern
    }

# ─── Task A — User Modeling ───────────────────────────────────────────────────

@app.post("/generate-review")
def generate_review(data: ReviewRequest):
    """
    Task A: Simulate how a specific user would review an unseen item.
    Uses their full review history from Yelp, Amazon, and Goodreads
    to model their tone, rating behaviour, and contextual nuance.
    """
    user = get_user_by_id(data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = simulate_review(
        user_id=data.user_id,
        item_name=data.item_name,
        item_category=data.item_category,
        item_description=data.item_description
    )

    pattern = get_rating_pattern(data.user_id)

    return {
        "user_id": data.user_id,
        "user_name": user["name"],
        "item": data.item_name,
        "simulated_rating": result["rating"],
        "simulated_review": result["review"],
        "confidence": result["confidence"],
        "reasoning": result["reasoning"],
        "user_rating_pattern": pattern
    }

# ─── Task B — Recommendation ──────────────────────────────────────────────────

@app.post("/get-recommendations")
def recommend(data: RecommendRequest):
    """
    Task B: Deliver personalised recommendations tailored to user context.
    Handles cold-start, cross-domain, and multi-turn scenarios.
    Uses Yelp + Amazon + Goodreads data for cross-domain recommendations.
    """
    result = get_recommendations(
        user_id=data.user_id,
        category=data.category,
        context=data.context,
        conversation_history=data.conversation_history
    )

    user = get_user_by_id(data.user_id)
    is_cold_start = user is None

    return {
        "user_id": data.user_id,
        "category": data.category,
        "is_cold_start": is_cold_start,
        "recommendations": result["recommendations"],
        "agent_insight": result["insight"],
        "total_recommendations": result["total"]
    }

# ─── Health Check ─────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    users = get_all_users()
    return {
        "status": "healthy",
        "message": "Naija Agent is live",
        "total_users": len(users),
        "datasets": ["Yelp", "Amazon Reviews", "Goodreads"],
        "tasks": ["Task A — User Modeling", "Task B — Recommendation"]
    }