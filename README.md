# cloudminiproject

## 🎓 AI-Based Career Recommendation System

An intelligent machine learning web application that predicts career paths, performs skill gap analysis, extracts skills from resumes, and visualizes comprehensive workforce analytics.

### 🌟 Key Features
- **Machine Learning Inference**: Predicts the best-fit career path along with calibrated confidence scores.
- **Skill Gap & Learning Roadmap**: Identifies missing critical skills and generates a targeted upskilling roadmap with certifications.
- **Interactive EDA Dashboard**: Visualizes career demand, education distribution, skill-to-career affinity, and workforce dataset metrics.
- **Resume Skill Extraction**: Parses raw resume text or job descriptions to automatically extract competencies.
- **Ready for Cloud Deployment**: Preconfigured for AWS (App Runner, EC2 Docker), Render, Railway, and Docker.

---

### 💻 Running Locally

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Nikeetk/cloudminiproject.git
   cd cloudminiproject
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the web application**:
   ```bash
   python app.py
   ```
   Open `http://localhost:8000` in your web browser.

---

### ☁️ AWS Cloud Deployment

- **AWS App Runner**: Connect this GitHub repository directly to AWS App Runner. It uses [apprunner.yaml](apprunner.yaml) to automatically build and deploy with full SSL.
- **AWS EC2 (Docker)**: Run `docker-compose up -d --build` on an Ubuntu EC2 instance.
- See [AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md) for full step-by-step instructions.

---

### 📁 Project Structure
- `app.py`: FastAPI web server & REST API endpoints.
- `recommendation_engine.py`: Machine learning recommendation logic & feature processing.
- `career_model.joblib`: Trained ML model artifacts.
- `career_metadata.json`: Salary, demand, certifications, and portfolio project metadata.
- `AI-based Career Recommendation System.csv`: Dataset used for analytics and training.
- `static/`: Frontend single-page application (HTML, CSS, JS).
- `Dockerfile` & `docker-compose.yml`: Container definitions.
- `apprunner.yaml`: AWS App Runner deployment configuration.
