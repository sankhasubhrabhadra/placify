<div align="center">
  <img src="https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/brain-circuit.svg" width="80" height="80" alt="Placify Logo">
  <h1>🚀 Placify</h1>
  <p><strong>Your Personal AI Interviewer & Technical Learning Platform</strong></p>
</div>

---

## About Placify

Placify is an AI-powered talent intelligence platform that connects every stage 
of interview and career prep into one place, instead of leaving candidates to 
juggle separate tools for each step.

### What it does

- **AI Mock Interviews** — live simulated technical and HR interview sessions with AI-generated questions, feedback, and real-time webcam posture/expression analysis.
- **Coding Problem Practice** — a structured problem bank with an integrated code editor for sandbox execution.
- **Skill Simulator** — a "what if" tool that simulates rapid-fire technical questions tailored to specific roles to help you gauge readiness quickly.
- **Learning Roadmaps** — personalized study paths tied directly to identified skill gaps (e.g., Data Structures, Frontend Architecture).
- **AI Coach** — a conversational assistant available throughout the platform for hints, guidance, and prep questions.

These aren't disconnected features — they all feed into one shared candidate 
profile and one explainable scoring engine.

### What makes it different

- **Verified, not just claimed** — skills are cross-checked against 
  the candidate's actual solved-problem history from the coding practice 
  module, instead of trusting text at face value.
- **Explainable, not just scored** — every decision comes with a confidence 
  breakdown and named reasons, drawing on coding performance, and 
  interview signals together, instead of a single opaque number.
- **Prescriptive, not just descriptive** — a "what if I learn X" simulator 
  shows the marginal score impact of closing any specific skill gap, and 
  routes directly into the matching learning roadmap.
- **One connected loop** — practice → mock interview → coach → 
  reassess, all on the same profile, instead of separate disconnected tools.

### Problem it addresses

Job prep today is fragmented across coding practice sites, interview prep tools, and learning platforms that don't talk to each other. Rejections happen with no explanation, interview practice is either unstructured or purely mechanical, and skill-gap advice is generic rather than tied to a specific role or a candidate's actual demonstrated performance.

### Who it's for

- **Candidates** — especially students at colleges with limited access to structured career guidance or mock-interview practice
- **Recruiters/hiring teams** — who need fast, defensible, auditable shortlisting decisions
- **Educational institutions** — who need aggregate skill-gap visibility to inform curriculum

### Tech stack

- **Backend:** Flask (Python), modular engines for coding assessment, interview logic, scoring, and explanation.
- **AI:** Local Ollama engine. Uses `qwen2.5:1.5b` for lightning-fast interview generation and `moondream` for local webcam/vision posture analysis—keeping all data entirely private.
- **Security:** Sandboxed code execution (memory-capped, network-restricted) for the practice module.
- **Frontend:** Vanilla HTML/CSS/JS + Chart.js for data visualization.
- **Deployment:** Vercel (frontend) proxied to the local backend using a secure Cloudflare Quick Tunnel (`cloudflared`).

---

## 🚀 Setup & Running Locally

1. **Start the Local AI Engine**: Pull the models and start Ollama:
   ```bash
   ollama run qwen2.5:1.5b
   ollama run moondream
   ollama serve
   ```
2. **Boot up the Backend**: Start the Flask API:
   ```bash
   python app.py
   ```
3. **Expose the Backend Securely**: Run a Cloudflare tunnel:
   ```bash
   cloudflared tunnel --url http://localhost:5000 --protocol http2
   ```
4. **Connect the Frontend**: Update `frontend/vercel.json` with your generated Cloudflare URL, and deploy via Vercel.
