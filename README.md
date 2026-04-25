# 🤖 AI-Powered Talent Scouting & Engagement Agent

An AI agent that takes a Job Description as input, discovers matching candidates, simulates conversational outreach, and outputs a ranked shortlist scored on Match Score and Interest Score.

## Features
- JD Parsing using LLM
- Candidate matching with explainability
- Simulated conversational outreach
- Ranked shortlist with Match & Interest scores

## Tech Stack
- Python
- Streamlit
- Groq API (LLaMA 3.3)

## How to Run
1. Clone the repo
2. Install dependencies: `pip install streamlit groq pandas`
3. Add your Groq API key in `.streamlit/secrets.toml`
4. Run: `streamlit run app.py`

## Architecture
JD Input → JD Parser → Candidate Matcher → Outreach Simulator → Ranked Output
