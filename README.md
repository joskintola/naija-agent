# 🇳🇬 Naija Agent
### LLM-Powered User Modelling & Personalised Recommendation System
**DSN × Bluechip Technologies — LLM Agent Challenge · Hackathon 3.0**

---

## 🔗 Live Application
**[https://naija-agent-production.up.railway.app](https://naija-agent-production.up.railway.app)**

---

## 📌 Overview

Naija Agent is a two-task LLM-based system that models Nigerian user behaviour and delivers personalised cross-domain recommendations. It is built on real data from **Yelp**, **Amazon Reviews**, and **Goodreads**, powered by **Claude claude-opus-4-5**, and contextualised deeply for Nigerian users, language, and culture.

| Task | Description |
|------|-------------|
| **Task A — User Modelling** | Simulates how a specific user would review an unseen item — capturing their tone, rating behaviour, vocabulary, and Nigerian cultural context |
| **Task B — Recommendation** | Delivers personalised cross-domain recommendations using chain-of-thought reasoning, handling cold-start users and multi-turn refinement |

---

## 🏗️ Architecture
---

naija-agent/
├── app/
│   ├── main.py          # FastAPI endpoints — Task A and Task B
│   ├── agent.py         # AI brain — Claude API + prompt engineering
│   ├── data.py          # Dataset loader — Yelp, Amazon, Goodreads
│   ├── index.html       # Single-page frontend UI
│   └── data/
│       ├── yelp_sample.json       # 26 users, 452 Nigerian businesses
│       ├── amazon_sample.json     # 50 users, 473 products
│       └── goodreads_sample.json  # 46 users, 200 books
├── extract_data.py      # One-time data extraction pipeline
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container definition
├── docker-compose.yml   # Multi-service orchestration
└── README.md
## 📊 Datasets
---
| Dataset | Source | Users | Items | Domain |
|---------|--------|-------|-------|--------|
| Yelp | Kaggle (yelp-dataset) | 26 | 452 businesses | Food & Restaurants |
| Amazon Reviews | Kaggle (amazon-product-reviews) | 50 | 473 products | Products & Shopping |
| Goodreads | Kaggle (goodreadsbooks) | 46 | 200 books | Books & Entertainment |

All datasets are publicly available. Users are unified across datasets into cross-domain profiles for genuine cross-domain recommendation.

---

## 🚀 Running Locally

### Option 1 — Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/joskintola/naija-agent.git
cd naija-agent

# Create .env file
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Build and run
docker build -t naija-agent .
docker run -p 8000:8000 --env-file .env naija-agent
```

Open [http://localhost:8000](http://localhost:8000)

### Option 2 — Python directly

```bash
# Clone the repository
git clone https://github.com/joskintola/naija-agent.git
cd naija-agent

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Run
uvicorn app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000)

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Claude API key from console.anthropic.com |

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /` | GET | Main web interface |
| `GET /users` | GET | List all users across all datasets |
| `GET /users/{user_id}` | GET | Full profile and rating pattern for a user |
| `POST /generate-review` | POST | Task A: Simulate user review for unseen item |
| `POST /get-recommendations` | POST | Task B: Cross-domain personalised recommendations |
| `GET /health` | GET | System health and dataset statistics |

### Task A — Example Request
```json
POST /generate-review
{
  "user_id": "rLtl8ZkDX5vH5nAx9C3q5Q",
  "item_name": "Chicken Republic Lekki",
  "item_category": "Fast Food",
  "item_description": "Popular Nigerian fast food chain known for fried chicken and chips"
}
```

### Task A — Example Response
```json
{
  "user_name": "User rLtl8Z",
  "simulated_rating": "4",
  "simulated_review": "This place don try sha. The chicken was fresh and properly seasoned...",
  "confidence": "HIGH",
  "reasoning": "User historically rates quality fast food at 4 stars and praises freshness",
  "user_rating_pattern": {
    "avg": 3.8,
    "min": 2,
    "max": 5,
    "count": 5,
    "tendency": "balanced — rates fairly based on actual experience"
  }
}
```

### Task B — Example Request
```json
POST /get-recommendations
{
  "user_id": "rLtl8ZkDX5vH5nAx9C3q5Q",
  "category": "Restaurants in Lagos",
  "context": "Looking for something special this weekend",
  "conversation_history": []
}
```

---

## Nigerian Context


- **Language** — Agent produces authentic Nigerian Pidgin English, city-specific references, and demographic-specific vocabulary
- **Geography** — Covers Lagos, Abuja, Ibadan, Port Harcourt, and Kano with distinct cultural personalities
- **Economics** — Captures Nigerian economic realities: naira pricing, NEPA blackouts, budget sensitivity by demographic
- **Cross-cultural intelligence** — Recommends Nigerian music, local restaurants, and culturally relevant books based on inferred taste profiles

---

## 🤖 Agent Design

### Task A — Behavioural Simulation Protocol
1. Full review history injected (Yelp + Amazon + Goodreads)
2. Rating pattern computed and injected (avg, range, tendency)
3. Behavioural reasoning instruction (tone, vocabulary, cultural markers)
4. Structured 4-field output: `RATING` / `REVIEW` / `CONFIDENCE` / `REASONING`

### Task B — Chain-of-Thought Recommendation Protocol
1. Profile analysis — what does history reveal about taste and budget?
2. Pattern extraction — consistent loves and disappointments
3. Cross-domain mapping — preference transfer across food, products, books
4. Ranked output — 5 recommendations with match scores and history-based reasoning
5. Agent Insight — transparent summary of user model

---

## 🧪 Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.11, FastAPI, Uvicorn |
| AI Model | Claude claude-opus-4-5 (Anthropic) |
| Data | Yelp, Amazon Reviews, Goodreads (via Kaggle) |
| Frontend | Vanilla HTML/CSS/JavaScript |
| Container | Docker |
| Deployment | Railway |

---

## 📄 Solution Paper

The  solution paper covering approach, architecture decisions, experiments, ablation studies, and future work is included in the submission.

---

## 👤 Author

**Joseph Akintola**  
Engineering Student, University of Lagos  
DSN × BCT LLM Agent Challenge — Hackathon 3.0 · May 2026

---

* Datasets: Yelp (Kaggle), Amazon Reviews (Kaggle), Goodreads (Kaggle). Use of public pre-trained models and additional datasets.*
