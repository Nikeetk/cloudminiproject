# 🚀 Deployment Guide: AI-Based Career Recommendation System

This project contains everything needed to deploy the **FastAPI + ML Model + Interactive Web UI** to the cloud or via Docker.

---

## ⚡ Option 1: Deploy to Render (Recommended — Free & Easiest)

Render is the simplest platform to deploy Python web applications for free.

### Step 1: Push Project to GitHub
1. Create a new GitHub repository (e.g., `ai-career-recommendation-system`).
2. Inside your project folder, initialize git and push:
   ```bash
   cd "/Users/nikeetkumar/Carrer prediction system"
   git init
   git add .
   git commit -m "Initial commit for deployment"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```

### Step 2: Deploy on Render
1. Go to [dashboard.render.com](https://dashboard.render.com/) and sign in with GitHub.
2. Click **New +** -> **Web Service**.
3. Select your GitHub repository (`ai-career-recommendation-system`).
4. Configure settings (or Render will automatically detect `render.yaml`):
   - **Name**: `ai-career-recommendation`
   - **Environment**: `Python 3`
   - **Region**: Choose the closest region (e.g., Singapore, Oregon, Frankfurt)
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
5. Click **Create Web Service**.
6. Render will build and deploy your app. You'll get a public URL like:
   `https://ai-career-recommendation.onrender.com`

---

## 🤗 Option 2: Deploy to Hugging Face Spaces (100% Free for ML)

Hugging Face Spaces is designed specifically for machine learning web apps.

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Set:
   - **Space name**: `career-recommendation-system`
   - **Space SDK**: **Docker** (Blank)
   - **License**: Apache 2.0 / MIT
   - **Space hardware**: Free CPU (16 GB RAM)
3. Clone your Space repository locally or push the files directly using Git:
   ```bash
   git remote add hf https://huggingface.co/spaces/<your-username>/career-recommendation-system
   git push hf main
   ```
4. Hugging Face will automatically build your `Dockerfile` and host it live with a public URL!

---

## 🚂 Option 3: Deploy to Railway

1. Go to [railway.app](https://railway.app/) and sign in.
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select your repository.
4. Railway will automatically detect the `Procfile` or `Dockerfile` and deploy with dynamic port bindings.

---

## 🐳 Option 4: Run via Docker (Locally or Cloud VM / Cloud Run / AWS)

Build and run the containerized application on any system with Docker:

### 1. Build the image:
```bash
docker build -t career-recommender:latest .
```

### 2. Run the container:
```bash
docker run -d -p 8000:8000 --name career-app career-recommender:latest
```

### 3. Open in browser:
Visit `http://localhost:8000`

---

## 📋 Included Deployment Files Summary

| File | Purpose |
| :--- | :--- |
| [requirements.txt](file:///Users/nikeetkumar/Carrer%20prediction%20system/requirements.txt) | Python dependencies (`fastapi`, `uvicorn`, `scikit-learn`, `pandas`, `joblib`, etc.) |
| [Dockerfile](file:///Users/nikeetkumar/Carrer%20prediction%20system/Dockerfile) | Container definition for multi-platform deployment |
| [.dockerignore](file:///Users/nikeetkumar/Carrer%20prediction%20system/.dockerignore) | Excludes caches and GUI files to minimize container image size |
| [Procfile](file:///Users/nikeetkumar/Carrer%20prediction%20system/Procfile) | Defines web process command for PaaS platforms (Heroku, Render, Railway) |
| [render.yaml](file:///Users/nikeetkumar/Carrer%20prediction%20system/render.yaml) | Infrastructure-as-code blueprint for Render |
| [.gitignore](file:///Users/nikeetkumar/Carrer%20prediction%20system/.gitignore) | Keeps repository clean of temporary python/OS files |
| [app.py](file:///Users/nikeetkumar/Carrer%20prediction%20system/app.py) | Dynamic `$PORT` and `$HOST` listening with static web UI serving |
