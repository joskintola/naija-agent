import anthropic
import os
from dotenv import load_dotenv
from app.data import get_user_by_id, get_user_summary, get_rating_pattern, get_all_businesses, get_all_products, get_all_books

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def simulate_review(user_id: str, item_name: str, item_category: str, item_description: str):
    """
    Task A — User Modeling
    Uses real user history from Yelp + Amazon + Goodreads
    to simulate how that specific user would review an unseen item.
    """
    user_summary = get_user_summary(user_id)
    rating_pattern = get_rating_pattern(user_id)

    if not user_summary:
        return cold_start_review(item_name, item_category, item_description)

    prompt = f"""You are an expert user behavior modeling agent. Your job is to simulate how a SPECIFIC real user would write a review — capturing their exact tone, vocabulary, rating tendency, and personality.

IMPORTANT: Study this user's complete review history carefully before responding. You must sound EXACTLY like this person.

{user_summary}

RATING BEHAVIOUR ANALYSIS:
- Average rating this user gives: {rating_pattern['avg']} out of 5
- Their rating tendency: {rating_pattern['tendency']}
- They have written {rating_pattern['count']} reviews total
- Their rating range: {rating_pattern['min']} to {rating_pattern['max']}

NEW ITEM TO REVIEW (this user has NOT reviewed this before):
- Item Name: {item_name}
- Category: {item_category}
- Description: {item_description}

YOUR TASK:
1. Study how this user writes — their sentence length, use of local expressions, level of detail, what they praise, what they criticise
2. Predict what star rating this specific user would give based on their rating pattern and preferences
3. Write a review in their exact voice and style

STRICT RULES:
- Match their exact writing style — if they use Pidgin, use Pidgin. If they are formal, be formal.
- The rating must be consistent with their rating history and tendency
- Reference specific details about the item that would matter to THIS user based on their history
- Do NOT write a generic review — it must sound like THIS specific person

Respond in this EXACT format:
RATING: [number 1-5]
REVIEW: [the simulated review in the user's exact voice]
CONFIDENCE: [HIGH/MEDIUM/LOW — how confident you are this matches the user's behaviour]
REASONING: [one sentence explaining why you gave this rating based on their history]"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    return parse_review_response(message.content[0].text)


def cold_start_review(item_name: str, item_category: str, item_description: str):
    """Handle cold start — new user with no history"""
    prompt = f"""You are a Nigerian user reviewing a product or place for the first time.
    
Item: {item_name}
Category: {item_category}
Description: {item_description}

Write an authentic Nigerian review with a star rating. Use natural Nigerian expressions and context.

Respond in this EXACT format:
RATING: [number 1-5]
REVIEW: [authentic Nigerian review]
CONFIDENCE: LOW
REASONING: Cold start user — generated based on general Nigerian consumer behaviour patterns"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )

    return parse_review_response(message.content[0].text)


def parse_review_response(text: str):
    """Parse the structured response from the agent"""
    lines = text.strip().split("\n")
    result = {
        "rating": "3",
        "review": "",
        "confidence": "MEDIUM",
        "reasoning": ""
    }

    for line in lines:
        if line.startswith("RATING:"):
            result["rating"] = line.replace("RATING:", "").strip()
        elif line.startswith("REVIEW:"):
            result["review"] = line.replace("REVIEW:", "").strip()
        elif line.startswith("CONFIDENCE:"):
            result["confidence"] = line.replace("CONFIDENCE:", "").strip()
        elif line.startswith("REASONING:"):
            result["reasoning"] = line.replace("REASONING:", "").strip()

    # Handle multi-line reviews
    if not result["review"]:
        capture = False
        review_lines = []
        for line in lines:
            if line.startswith("REVIEW:"):
                capture = True
                first = line.replace("REVIEW:", "").strip()
                if first:
                    review_lines.append(first)
            elif line.startswith("CONFIDENCE:") or line.startswith("REASONING:"):
                capture = False
            elif capture:
                review_lines.append(line)
        result["review"] = " ".join(review_lines).strip()

    return result


def get_recommendations(user_id: str, category: str, context: str = "", conversation_history: list = []):
    """
    Task B — Recommendation Agent
    Handles: personalised, cold-start, cross-domain, and multi-turn recommendations
    """
    user_summary = get_user_summary(user_id)
    rating_pattern = get_rating_pattern(user_id)

    # Build available items catalogue
    businesses = get_all_businesses()[:20]
    products = get_all_products()[:20]
    books = get_all_books()[:20]

    catalogue = f"""
AVAILABLE FOOD & RESTAURANT OPTIONS (Yelp):
{chr(10).join([f"- {b['name']} | {b['category']} | Rating: {b['rating_avg']} | {b['description']}" for b in businesses])}

AVAILABLE PRODUCTS (Amazon):
{chr(10).join([f"- {p['name']} | {p['category']} | ₦{p['price_naira']:,} | {p['description']}" for p in products])}

AVAILABLE BOOKS (Goodreads):
{chr(10).join([f"- {b['title']} by {b['author']} | {b['category']} | {b['description']}" for b in books])}
"""

    # Build conversation context for multi-turn
    convo_context = ""
    if conversation_history:
        convo_context = "\nPREVIOUS CONVERSATION:\n"
        for turn in conversation_history[-4:]:
            convo_context += f"{turn['role'].upper()}: {turn['content']}\n"

    if not user_summary:
        user_context = "NEW USER — No review history available. Use general Nigerian consumer preferences."
        is_cold_start = True
    else:
        user_context = user_summary
        is_cold_start = False

    prompt = f"""You are an intelligent Nigerian recommendation agent that reasons deeply about user preferences before recommending.

{"⚠️ COLD START MODE: This is a new user with no history. Infer preferences from their stated context." if is_cold_start else ""}

USER PROFILE & COMPLETE REVIEW HISTORY:
{user_context}

{"RATING PATTERN: Average " + str(rating_pattern['avg']) + "/5 | Tendency: " + rating_pattern['tendency'] if not is_cold_start else ""}

RECOMMENDATION REQUEST:
- Category requested: {category}
- Additional context: {context if context else "None provided"}
{convo_context}

AVAILABLE ITEMS CATALOGUE:
{catalogue}

YOUR REASONING PROCESS (think step by step):
1. What does this user's history tell us about their taste, budget sensitivity, and quality expectations?
2. What patterns emerge from their ratings — what do they love, what disappoints them?
3. Which items from the catalogue best match these patterns?
4. How does the Nigerian context affect these recommendations?
5. Are there cross-domain opportunities (e.g. a food lover might enjoy food-related books)?

DELIVER:
- 5 ranked recommendations with clear reasoning
- Each recommendation must reference something specific from the user's history
- Include at least one cross-domain recommendation if relevant
- Use natural Nigerian conversational tone

Respond in this EXACT format for each recommendation:
1. [Item Name] | [Category] | MATCH SCORE: [1-10]
REASON: [Specific reason referencing user history]

2. [Item Name] | [Category] | MATCH SCORE: [1-10]
REASON: [Specific reason referencing user history]

3. [Item Name] | [Category] | MATCH SCORE: [1-10]
REASON: [Specific reason referencing user history]

4. [Item Name] | [Category] | MATCH SCORE: [1-10]
REASON: [Specific reason referencing user history]

5. [Item Name] | [Category] | MATCH SCORE: [1-10]
REASON: [Specific reason referencing user history]

AGENT INSIGHT: [One paragraph summarising what you learned about this user and why these recommendations fit them]"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    return parse_recommendation_response(message.content[0].text)


def parse_recommendation_response(text: str):
    """Parse recommendations from agent response"""
    lines = text.strip().split("\n")
    recommendations = []
    insight = ""
    current_item = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("AGENT INSIGHT:"):
            insight = line.replace("AGENT INSIGHT:", "").strip()
        elif line[0].isdigit() and "|" in line:
            if current_item:
                recommendations.append(current_item)
            parts = line.split("|")
            name = parts[0].split(".", 1)[-1].strip() if parts else line
            category = parts[1].strip() if len(parts) > 1 else "General"
            match_score = parts[2].replace("MATCH SCORE:", "").strip() if len(parts) > 2 else "7"
            current_item = {
                "name": name,
                "category": category,
                "match_score": match_score,
                "reason": ""
            }
        elif line.startswith("REASON:") and current_item:
            current_item["reason"] = line.replace("REASON:", "").strip()

    if current_item:
        recommendations.append(current_item)

    return {
        "recommendations": recommendations,
        "insight": insight,
        "total": len(recommendations)
    }