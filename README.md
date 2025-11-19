# Jarvis Agent
A cloud-native, autonomous AI agent capable of executing Python code, manipulating files, and self-installing libraries.

## Features
- **Autonomous Python Execution**: Can write and run its own code to solve tasks.
- **Self-Healing**: Can install missing libraries dynamically (`!pip install`).
- **Modern UI**: Glassmorphism-styled React interface.
- **Cloud Ready**: Dockerized for easy deployment on Render.

## Deployment on Render
1. Fork/Push this repo to GitHub.
2. Create a new **Web Service** on Render.
3. Connect your repository.
4. Select **Docker** as the runtime.
5. Add Environment Variable: `GEMINI_API_KEY` (Get one from Google AI Studio).
6. Deploy!

## Local Development
- Backend: `uvicorn backend.main:app --reload`
- Frontend: `cd frontend && npm run dev`
