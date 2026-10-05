# Placify: AI Interviewer & Learning Platform

Placify is a comprehensive platform designed to help candidates prepare for technical interviews. It features AI-driven mock interviews, posture analysis, Leetcode-style coding practice, and skill simulations.

## Architecture

- **Frontend**: A sleek dashboard deployed on Vercel.
- **Backend**: A local Python Flask API.
- **AI Models**: Runs locally using Ollama (`qwen2.5:1.5b` for chat, `moondream` for vision analysis).
- **Networking**: Connects Vercel to the local backend using a Cloudflare Quick Tunnel.

## Features

- **AI Mock Interviews**: Pair programming and conversational interviews powered by a local LLM.
- **Vision & Posture Analysis**: The frontend captures webcam frames and uses local Vision AI to provide feedback on your body language and professionalism during the interview.
- **Learning Roadmaps**: Explore curated paths for Data Structures & Algorithms, Frontend Architecture, and more.
- **Coding Practice**: A built-in code editor for solving technical problems.

## Setup & Running Locally

1. **Start Ollama**: Ensure `ollama serve` is running and you have pulled `qwen2.5:1.5b` and `moondream`.
2. **Start Flask**:
   ```bash
   python app.py
   ```
3. **Start Cloudflare Tunnel**:
   ```bash
   cloudflared tunnel --url http://localhost:5000 --protocol http2
   ```
4. **Update Frontend**: Update `frontend/vercel.json` with the new Cloudflare tunnel URL generated in step 3. Push the changes to GitHub to trigger a Vercel deployment.
