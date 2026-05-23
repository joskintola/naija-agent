import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def load_dataset(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_all_users():
    yelp = load_dataset("yelp_sample.json")
    amazon = load_dataset("amazon_sample.json")
    goodreads = load_dataset("goodreads_sample.json")

    yelp_users = {u["user_id"]: u for u in yelp["users"]}
    amazon_users = {u["user_id"]: u for u in amazon["users"]}
    goodreads_users = {u["user_id"]: u for u in goodreads["users"]}

    all_user_ids = set(yelp_users) | set(amazon_users) | set(goodreads_users)

    unified_users = []
    for uid in sorted(all_user_ids):
        yelp_u = yelp_users.get(uid, {})
        amazon_u = amazon_users.get(uid, {})
        goodreads_u = goodreads_users.get(uid, {})

        base = yelp_u or amazon_u or goodreads_u
        unified_users.append({
            "user_id": uid,
            "name": base.get("name", "Unknown"),
            "location": base.get("location", "Nigeria"),
            "profile": base.get("profile", "Dataset user"),
            "yelp_reviews": yelp_u.get("review_history", []),
            "amazon_reviews": amazon_u.get("review_history", []),
            "goodreads_reviews": goodreads_u.get("review_history", []),
        })

    return unified_users

def get_user_by_id(user_id: str):
    users = get_all_users()
    for user in users:
        if user["user_id"] == user_id:
            return user
    return None

def get_user_summary(user_id: str):
    user = get_user_by_id(user_id)
    if not user:
        return None

    summary = f"""
USER PROFILE:
Name: {user['name']}
Location: {user['location']}
Background: {user['profile']}

FOOD & RESTAURANT REVIEW HISTORY (Yelp):
"""
    for r in user["yelp_reviews"]:
        summary += f"""
- {r['business_name']} ({r['category']}) — {r['rating']}/5 stars
  Review: "{r['review']}"
"""

    summary += "\nPRODUCT REVIEW HISTORY (Amazon):\n"
    for r in user["amazon_reviews"]:
        summary += f"""
- {r['product_name']} ({r['category']}) — {r['rating']}/5 stars
  Review: "{r['review']}"
"""

    summary += "\nBOOK REVIEW HISTORY (Goodreads):\n"
    for r in user["goodreads_reviews"]:
        summary += f"""
- {r['book_title']} by {r['author']} ({r['category']}) — {r['rating']}/5 stars
  Review: "{r['review']}"
"""

    return summary

def get_rating_pattern(user_id: str):
    user = get_user_by_id(user_id)
    if not user:
        return {"avg": 3.0, "min": 1, "max": 5, "count": 0, "tendency": "neutral"}

    all_ratings = []
    for r in user["yelp_reviews"]:
        all_ratings.append(r["rating"])
    for r in user["amazon_reviews"]:
        all_ratings.append(r["rating"])
    for r in user["goodreads_reviews"]:
        all_ratings.append(r["rating"])

    if not all_ratings:
        return {"avg": 3.0, "min": 1, "max": 5, "count": 0, "tendency": "neutral"}

    avg = sum(all_ratings) / len(all_ratings)

    if avg >= 4.2:
        tendency = "generous — tends to rate high when satisfied"
    elif avg <= 2.8:
        tendency = "critical — holds high standards and rates strictly"
    else:
        tendency = "balanced — rates fairly based on actual experience"

    return {
        "avg": round(avg, 2),
        "min": min(all_ratings),
        "max": max(all_ratings),
        "count": len(all_ratings),
        "tendency": tendency
    }

def get_all_businesses():
    yelp = load_dataset("yelp_sample.json")
    return yelp.get("businesses", [])

def get_all_products():
    amazon = load_dataset("amazon_sample.json")
    return amazon.get("products", [])

def get_all_books():
    goodreads = load_dataset("goodreads_sample.json")
    return goodreads.get("books", [])