<div align="center">
  <img src="https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/brain-circuit.svg" width="80" height="80" alt="Placify Logo">
  <h1>🚀 Placify</h1>
  <p><strong>Your Personal AI Interviewer & Technical Learning Platform</strong></p>
</div>

---

Placify is a comprehensive, local-first platform designed to help software engineers prepare for technical interviews. By leveraging powerful local Large Language Models (LLMs) and Vision AI, Placify offers an immersive, privacy-focused mock interview experience right from your own hardware.

## ✨ Key Features

- 🤖 **Interactive Mock Interviews**: Engage in back-and-forth technical interviews on any topic (System Design, Frontend, DSA).
- 📸 **Vision AI Posture Analysis**: The frontend securely captures webcam frames during your interview. A local Vision AI model analyzes your body language, eye contact, and professionalism to give you actionable feedback.
- 🎯 **Automated Scorecards**: After every interview, receive a detailed breakdown of your technical skills, areas for improvement, and presentation.
- 🗺️ **Learning Roadmaps**: Follow curated paths for Data Structures, Algorithms, and System Architecture.
- 💻 **Integrated Code Editor**: Practice algorithmic problems directly in the browser.

## 🏗️ Architecture

Placify is designed to be fully self-hosted, keeping your data and webcam feeds entirely private.

- **Frontend**: A sleek, modern dashboard hosted on [Vercel](https://vercel.com).
- **Backend API**: A lightweight `Flask` server running locally on your machine.
- **AI Engine**: Powered entirely by [Ollama](https://ollama.ai/).
  - `qwen2.5:1.5b`: Lightning-fast model handling all interview dialogue and scorecard generation.
  - `moondream`: A compact vision model for analyzing webcam frames.
- **Networking**: A Cloudflare Quick Tunnel securely connects the Vercel frontend to your local Flask backend.

## 🚀 Getting Started

To run Placify locally on your machine, follow these steps:

### 1. Start the Local AI Engine
Ensure you have Ollama installed, and pull the required models:
```bash
ollama run qwen2.5:1.5b
ollama run moondream
```
Once pulled, keep the Ollama server running:
```bash
ollama serve
```

### 2. Boot up the Backend
Navigate to your Placify directory and start the Flask API:
```bash
python app.py
```
*(The server will run on `http://localhost:5000`)*

### 3. Expose the Backend Securely
To allow the Vercel frontend to talk to your local backend, open a new terminal and run:
```bash
cloudflared tunnel --url http://localhost:5000 --protocol http2
```
*Note: Copy the generated `https://*.trycloudflare.com` URL.*

### 4. Connect the Frontend
Open the `frontend/vercel.json` file in this repository. Replace the `destination` URL with your newly generated Cloudflare tunnel link. 
Commit and push the changes to trigger a Vercel redeployment.

---
<div align="center">
  <i>Built with Flask, Vanilla JS, and Ollama. Happy Interviewing! 🎉</i>
</div>
