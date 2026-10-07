<div align="center">
  <img src="https://via.placeholder.com/150x150/1F2937/FFA116?text=Placify" alt="Placify Logo" width="120" height="120" style="border-radius: 20px;">
  <br/>
  <h1>🚀 Placify</h1>
  <p><strong>AI-Powered Talent Intelligence & Placement Preparation Platform</strong></p>
  
  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript" />
    <img src="https://img.shields.io/badge/scikit_learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="Scikit-Learn" />
    <img src="https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama" />
    <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
    <img src="https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white" alt="Vercel" />
  </p>
  
  <p><em>Developed for the SAS CU Hackathon</em></p>
</div>

---

## 📖 Table of Contents
- [About Placify](#-about-placify)
- [Key Features](#-key-features)
- [The Data Pipeline & Machine Learning](#-the-data-pipeline--machine-learning)
- [Technical Architecture](#-technical-architecture)
- [Running Locally](#-running-locally)

---

## 🎯 About Placify

Placement preparation today is highly fragmented. Candidates write code on LeetCode, parse resumes with ChatGPT, and guess their market value using generic Glassdoor data. Nothing talks to each other, and worse—candidates rarely know *which* skills actually drive salary hikes.

**Placify** solves this by unifying resume scanning, job market analytics, mock interviews, and personalized learning paths into one seamless dashboard. Driven by empirical data (over **17,000 real-world job postings** and **employee success metrics**), Placify doesn't just score you—it tells you *exactly* what to do next to maximize your career trajectory.

---

## ✨ Key Features

### 📄 Local, Data-Driven Resume Scanner
Extracts skills directly in your browser using `pdf.js` (no cloud upload required) and cross-references them against an index of 17,000+ real job postings. It calculates a realistic Fit Score, highlights missing high-demand skills, and predicts an estimated salary band.

### 🧮 "What If" Skill Simulator
Powered by a custom **Logistic Regression** model trained on Junior Data Scientist (JDS) traits. Adjust your technical skill sliders (Coding, Big Data, Maths/Stats) to see your real-time mathematical probability of securing a high salary hike, including the exact marginal gain of learning new skills.

### 🧠 Behavioural Readiness & AI Mock Interviews
Maps your "Big Five" personality traits to a Logistic Regression model trained on senior employee success data, providing percentile ranks and targeted development advice. Features live technical mock interviews powered by local LLMs (`qwen2.5`) and real-time webcam posture analysis (`moondream`).

### 🗺️ Data-Ranked Learning Paths
Stop guessing what to study. Placify automatically ranks learning modules using a custom algorithm: **Market Demand** (frequency in job postings) + **Outcome Impact** (Logistic Regression weight). 

### 📊 Live Job Market Intelligence
An interactive `Chart.js` dashboard showcasing the top hiring companies, highest-demand cities, and precise salary ranges across data science roles.

---

## 🧬 The Data Pipeline & Machine Learning

Placify is not just a UI wrapper—it is driven by an automated Data ETL and ML training pipeline.

1. **The Dataset:** We utilize four core datasets containing over 17,000 data science/analytics job postings, as well as employee behavioral and technical trait scoring datasets.
2. **Data Cleaning:** The pipeline normalizes job titles, maps salary strings to numerical LPAs, splits comma-separated locations, and standardizes skills.
3. **Model Training:** `scikit-learn` trains predictive Logistic Regression models targeting salary hikes and overall success metrics.
4. **Edge Deployment:** Instead of running heavy Python models per user request, the script exports model weights, coefficients, and market distributions as highly optimized JSON files directly to the frontend. The browser handles the complex math locally, ensuring lightning-fast performance.

---

## 🏗️ Technical Architecture

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | Vanilla JS, HTML, CSS | Ultra-lightweight static frontend with `Chart.js` for data visualization. |
| **Hosting** | Vercel | Globally distributed edge hosting for the frontend. |
| **Backend API** | Python, Flask | Modular engines for coding sandbox execution and AI routing. |
| **Data Pipeline** | Pandas, Scikit-Learn | ETL pipeline that cleans CSVs and trains ML models, exporting to JSON. |
| **AI Models** | Ollama | 100% local, private AI (`qwen2.5:1.5b` for NLP, `moondream` for Vision). |
| **Networking** | Cloudflare Tunnels | Secure HTTP2 tunnels connecting the public Vercel frontend to the private local AI backend. |

---

## 🚀 Running Locally

Want to run the full stack on your own machine? Follow these steps:

### 1. Start the Local AI Engine
You will need [Ollama](https://ollama.com/) installed to run the private AI models.
```bash
ollama pull qwen2.5:1.5b
ollama pull moondream
ollama serve
```

### 2. Boot up the Backend
Install the Python dependencies and start the Flask API server:
```bash
pip install -r requirements.txt
python app.py
```

### 3. Expose the Backend Securely
Because Vercel requires HTTPS endpoints, we use Cloudflare Tunnels to expose your local Flask server securely without opening ports:
```bash
cloudflared tunnel --url http://localhost:5000 --protocol http2
```

### 4. Configure the Frontend
1. Copy the generated `trycloudflare.com` URL from step 3.
2. Update the API endpoints in `frontend/script.js` and `frontend/vercel.json` with your new tunnel URL.
3. Deploy the `frontend/` directory to Vercel!

### 5. Update Market Data
To retrain the ML models and update the Job Market dashboard with fresh CSV data:
1. Place your data files inside your defined `UPLOAD_DIR` (configured in the script).
2. Run the ETL pipeline:
```bash
python scripts/prepare_data.py
```
3. The frontend will dynamically fetch the newly generated JSON files. No server restart required!

---
<div align="center">
  <i>Built with ❤️ for the SAS CU Hackathon</i>
</div>
