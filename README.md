# 📰 Daily News Brief Generator

A personalized AI-powered daily news brief app built for Vibeathon 2.0.

## Features
- 🔍 Fetches news from NewsAPI + RSS feeds across 6 categories
- 🤖 AI-powered summaries using Groq (Llama 3.1)
- 📅 Browse past briefs by date
- ⚙️ Personalized category and reading style preferences
- 🚀 Deployed on Streamlit Cloud + Render

## Tech Stack
- **Frontend**: Streamlit
- **Backend**: FastAPI + Uvicorn
- **AI**: Groq API (Llama 3.1 8B)
- **News Sources**: NewsAPI, RSS Feeds

## Setup

1. Clone the repo
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate`
4. Install: `pip install -r requirements.txt`
5. Create `.env` with your API keys:

NEWS_API_KEY=your_key
GROQ_API_KEY=your_key
6. Run backend: `uvicorn backend.main:app --reload`
7. Run frontend: `streamlit run frontend/app.py`

## Deployment
- Backend: Render.com
- Frontend: Streamlit Cloud