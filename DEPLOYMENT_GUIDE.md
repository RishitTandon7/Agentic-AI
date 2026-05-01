# AURA Agentic AI - Deployment Guide

This project consists of a Python/Flask backend with an HTML frontend, Playwright for web scraping, and integrations with LLMs (Gemini, Llama) and Google/SerpApi Search APIs.

Because the system relies on headless browser automation (Playwright), the most robust and hassle-free way to deploy is using **Docker**.

## 1. Prerequisites (Environment Setup)

Before deploying to any platform, you will need to configure your environment variables. Ensure you have the following secrets ready to be added to your hosting provider's dashboard:

* `GOOGLE_API_KEY`: Your Google Cloud API Key
* `GOOGLE_CX` / `SEARCH_ENGINE_ID`: Custom Search Engine ID
* `SERPAPI_KEY`: Your SerpApi Key
* `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, etc.: Gemini API Keys (if using key rotation)

## 2. Docker Setup (Recommended)

I have created a `Dockerfile` and a `requirements_prod.txt` at the root of the repository.

*   **Base Image:** The Dockerfile uses `mcr.microsoft.com/playwright/python:v1.40.0-jammy` to ensure all system-level dependencies for Chromium are installed.
*   **WSGI Server:** We've included `gunicorn` to serve the Flask app (`web_app:app`) securely in production, replacing Flask's built-in development server.
*   **Persistent Storage:** The Dockerfile creates a `data/` directory.

## 3. Recommended Hosting Platforms

### Option A: Render (Best for ease of use)

1. Sign up/Log in to [Render](https://render.com/).
2. Click **New +** and select **Web Service**.
3. Connect your GitHub repository (`RishitTandon7/Agentic-AI`).
4. **Environment setup:**
    * Environment: `Docker` (Render will automatically detect the `Dockerfile`).
    * Branch: `main`
5. **Advanced / Persistent Disk:**
    * Scroll down to **Advanced** -> **Add Disk**.
    * Name: `aura-data`, Mount Path: `/app/data`, Size: `1 GB`. (This ensures `.products.csv` and history persist across restarts).
6. **Environment Variables:**
    * Add all the keys listed in Step 1.
7. Click **Create Web Service**. Render will build the Docker container and deploy your app.

### Option B: Railway.app

1. Sign up/Log in to [Railway](https://railway.app/).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select `RishitTandon7/Agentic-AI`.
4. Railway will automatically detect the `Dockerfile` and start building.
5. Go to the **Variables** tab in your Railway project to add all your API keys.
6. Under **Settings** -> **Networking**, generate a custom domain to access your application.

### Option C: AWS EC2 / DigitalOcean Droplet (Manual VPS)

If you prefer a raw Linux server (Ubuntu 22.04+):
1. SSH into your server.
2. Clone the repository.
3. Install Docker and Docker Compose.
4. Run:
   ```bash
   docker build -t aura-app .
   docker run -d -p 80:5001 --env-file .env -v aura_data:/app/data --name aura-container aura-app
   ```

## 4. How to Use Local LLMs (Ollama) in Production

Because Ollama runs large AI models (like Llama 3.2), it requires significant compute power (specifically GPUs or high-end CPUs). Standard, cheap cloud tiers (like Render or Railway basic plans) will likely crash if you try to run Ollama directly on them.

If you are hosting this project and want to use the Ollama fallback, you have **three main options**:

### Option 1: GPU-Enabled Cloud Server (Full Control)
Instead of using a simple service like Render, rent a GPU-enabled server (e.g., **AWS EC2 g4dn.xlarge**, **RunPod**, or **Paperspace**). 
1. Install Docker on the server.
2. Install Ollama directly on the server host and run `ollama pull llama3.2`.
3. Deploy the app's Docker container on the same server, and it will communicate with the host's Ollama instance.

### Option 2: The Hybrid Approach (Host App in Cloud, Ollama on your PC)
You can deploy your Flask app cheaply on Render, but configure it to talk to the Ollama instance running on your powerful local home computer.
1. Run Ollama on your home PC.
2. Expose your local Ollama port (11434) to the internet using **Ngrok** (`ngrok http 11434`).
3. In your Render app environment variables, point the `OLLAMA_HOST` variable to your Ngrok URL.
*Note: Your home PC must be turned on for this to work.*

### Option 3: Replace Ollama with a Fast API (Groq / Together AI)
If you don't want to manage expensive GPUs, you can change the codebase to use **Groq** or **Together AI**. These providers host Llama 3.2 for you via an API, which is much cheaper and infinitely faster than running it yourself. You would simply replace the `ollama.chat()` calls in `judge_agent.py` with requests to the Groq API.

*If you do nothing, the app will safely ignore Ollama failures in the cloud and automatically fall back to your Gemini API keys.*
