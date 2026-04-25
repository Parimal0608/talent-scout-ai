import streamlit as st
from groq import Groq
import pandas as pd
import json

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

CANDIDATES = [
    {"name": "Aarav Shah", "skills": ["Python", "Machine Learning", "TensorFlow", "SQL"], "experience": 4, "location": "Bangalore", "current_role": "ML Engineer"},
    {"name": "Priya Menon", "skills": ["Python", "NLP", "Hugging Face", "PyTorch"], "experience": 3, "location": "Hyderabad", "current_role": "Data Scientist"},
    {"name": "Rohan Verma", "skills": ["Java", "Spring Boot", "AWS", "Microservices"], "experience": 5, "location": "Pune", "current_role": "Backend Engineer"},
    {"name": "Sneha Iyer", "skills": ["React", "Node.js", "MongoDB", "TypeScript"], "experience": 2, "location": "Chennai", "current_role": "Full Stack Developer"},
    {"name": "Karan Patel", "skills": ["Python", "Deep Learning", "Computer Vision", "OpenCV"], "experience": 6, "location": "Mumbai", "current_role": "AI Researcher"},
    {"name": "Divya Nair", "skills": ["Data Analysis", "SQL", "Tableau", "Python"], "experience": 3, "location": "Bangalore", "current_role": "Data Analyst"},
    {"name": "Arjun Khanna", "skills": ["Machine Learning", "Python", "Scikit-learn", "Flask"], "experience": 2, "location": "Delhi", "current_role": "Junior ML Engineer"},
    {"name": "Meera Joshi", "skills": ["NLP", "Python", "BERT", "LangChain", "LLMs"], "experience": 5, "location": "Bangalore", "current_role": "NLP Engineer"},
    {"name": "Vikram Bose", "skills": ["AWS", "Docker", "Kubernetes", "DevOps", "Python"], "experience": 7, "location": "Hyderabad", "current_role": "DevOps Engineer"},
    {"name": "Ananya Das", "skills": ["Python", "Machine Learning", "SQL", "Power BI"], "experience": 4, "location": "Kolkata", "current_role": "ML Engineer"}
]

def ask_groq(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def parse_jd(jd_text):
    prompt = f"""
Parse this job description and extract key information.
Return ONLY a JSON object with these fields:
- title: job title
- required_skills: list of required skills
- experience_min: minimum years of experience (number)
- key_requirements: list of 3 key requirements

Job Description:
{jd_text}

Return only valid JSON, nothing else.
"""
    text = ask_groq(prompt)
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)

def calculate_match_score(candidate, jd_parsed):
    required_skills = [s.lower() for s in jd_parsed.get("required_skills", [])]
    candidate_skills = [s.lower() for s in candidate["skills"]]
    skill_matches = sum(1 for skill in required_skills if any(skill in cs or cs in skill for cs in candidate_skills))
    skill_score = (skill_matches / max(len(required_skills), 1)) * 60
    exp_min = jd_parsed.get("experience_min", 0)
    if candidate["experience"] >= exp_min:
        exp_score = 40
    elif candidate["experience"] >= exp_min - 1:
        exp_score = 25
    else:
        exp_score = 10
    total = min(100, int(skill_score + exp_score))
    matched = [s for s in jd_parsed.get("required_skills", []) if any(s.lower() in cs.lower() or cs.lower() in s.lower() for cs in candidate["skills"])]
    reason = f"Matched skills: {', '.join(matched) if matched else 'None'}. Experience: {candidate['experience']} years."
    return total, reason

def simulate_outreach(candidate, jd_parsed):
    prompt = f"""
You are a recruiter chatbot reaching out to a candidate for a job.

Candidate: {candidate['name']}, {candidate['experience']} years experience, current role: {candidate['current_role']}
Job: {jd_parsed.get('title', 'AI Role')}
Required skills: {', '.join(jd_parsed.get('required_skills', []))}

Simulate a short 3-message conversation where you:
1. Reach out to the candidate
2. Candidate responds showing their interest level
3. You ask one follow-up question and candidate responds

Based on the conversation, give an Interest Score from 0-100.

Return ONLY a JSON object with:
- conversation: list of messages with 'sender' and 'message' fields
- interest_score: number 0-100
- interest_reason: one sentence explanation

Return only valid JSON, nothing else.
"""
    text = ask_groq(prompt)
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)

st.set_page_config(page_title="AI Talent Scout", page_icon="🤖", layout="wide")
st.title("🤖 AI-Powered Talent Scouting & Engagement Agent")
st.markdown("*Paste a Job Description → Get a ranked shortlist of candidates with Match & Interest scores*")

with st.sidebar:
    st.header("📋 How it works")
    st.markdown("""
1. Paste your Job Description
2. AI parses the JD
3. Candidates are matched & scored
4. AI simulates outreach conversations
5. Get a ranked shortlist!
""")
    st.info(f"👥 Candidate pool: {len(CANDIDATES)} profiles")

jd_input = st.text_area("📝 Paste Job Description here:", height=200, placeholder="e.g. We are looking for a Machine Learning Engineer with 3+ years of experience in Python, TensorFlow...")

if st.button("🚀 Find & Rank Candidates", type="primary"):
    if not jd_input.strip():
        st.error("Please paste a job description first!")
    else:
        with st.spinner("🔍 Parsing job description..."):
            try:
                jd_parsed = parse_jd(jd_input)
                st.success(f"✅ JD Parsed: **{jd_parsed.get('title', 'Role')}**")
                with st.expander("See parsed JD details"):
                    st.json(jd_parsed)
            except Exception as e:
                st.error(f"Error parsing JD: {e}")
                st.stop()

        results = []
        progress = st.progress(0)
        status = st.empty()

        for i, candidate in enumerate(CANDIDATES):
            status.text(f"Analyzing {candidate['name']}...")
            match_score, match_reason = calculate_match_score(candidate, jd_parsed)
            progress.progress((i + 1) / len(CANDIDATES))
            results.append({
                "name": candidate["name"],
                "current_role": candidate["current_role"],
                "experience": candidate["experience"],
                "skills": ", ".join(candidate["skills"]),
                "match_score": match_score,
                "match_reason": match_reason,
                "location": candidate["location"]
            })

        top_candidates = sorted(results, key=lambda x: x["match_score"], reverse=True)[:5]
        status.text("💬 Simulating outreach conversations for top candidates...")
        final_results = []

        for i, candidate_data in enumerate(top_candidates):
            candidate_obj = next(c for c in CANDIDATES if c["name"] == candidate_data["name"])
            try:
                outreach = simulate_outreach(candidate_obj, jd_parsed)
                candidate_data["interest_score"] = outreach.get("interest_score", 50)
                candidate_data["interest_reason"] = outreach.get("interest_reason", "")
                candidate_data["conversation"] = outreach.get("conversation", [])
            except:
                candidate_data["interest_score"] = 50
                candidate_data["interest_reason"] = "Could not simulate"
                candidate_data["conversation"] = []
            candidate_data["combined_score"] = int(0.6 * candidate_data["match_score"] + 0.4 * candidate_data["interest_score"])
            final_results.append(candidate_data)

        final_results = sorted(final_results, key=lambda x: x["combined_score"], reverse=True)
        progress.empty()
        status.empty()

        st.header("🏆 Ranked Candidate Shortlist")
        df = pd.DataFrame([{
            "Rank": i+1,
            "Name": r["name"],
            "Current Role": r["current_role"],
            "Experience (yrs)": r["experience"],
            "Location": r["location"],
            "Match Score": f"{r['match_score']}/100",
            "Interest Score": f"{r['interest_score']}/100",
            "Combined Score": f"{r['combined_score']}/100"
        } for i, r in enumerate(final_results)])
        st.dataframe(df, use_container_width=True)

        st.header("📊 Detailed Candidate Profiles")
        for i, r in enumerate(final_results):
            with st.expander(f"#{i+1} {r['name']} — Combined Score: {r['combined_score']}/100"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Match Score", f"{r['match_score']}/100")
                col2.metric("Interest Score", f"{r['interest_score']}/100")
                col3.metric("Combined Score", f"{r['combined_score']}/100")
                st.markdown(f"**Skills:** {r['skills']}")
                st.markdown(f"**Match Reason:** {r['match_reason']}")
                st.markdown(f"**Interest Reason:** {r['interest_reason']}")
                if r["conversation"]:
                    st.markdown("**💬 Simulated Outreach Conversation:**")
                    for msg in r["conversation"]:
                        if msg.get("sender") == "Recruiter":
                            st.markdown(f"🤝 **Recruiter:** {msg.get('message', '')}")
                        else:
                            st.markdown(f"👤 **{r['name']}:** {msg.get('message', '')}")