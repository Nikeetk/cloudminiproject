# ☁️ AWS Deployment Guide: AI-Based Career Recommendation System

This guide walks you through deploying your Career Recommendation application to **Amazon Web Services (AWS)** using the best and most reliable options.

---

## 🎯 Which AWS Option Should You Choose?

| Option | Ease of Use | Cost / Free Tier | Best For |
| :--- | :--- | :--- | :--- |
| **Option 1: AWS App Runner** | ⭐⭐⭐⭐⭐ Easiest | Pay-as-you-go | Fully managed, HTTPS included, zero server maintenance |
| **Option 2: AWS EC2 (Docker)** | ⭐⭐⭐ Medium | 750 hrs/month Free Tier | Complete control, runs directly on a virtual machine |
| **Option 3: AWS Elastic Beanstalk** | ⭐⭐⭐⭐ Easy | Underlying EC2 costs | Managed platform with automated load balancing |

---

## 🚀 Option 1: AWS App Runner (Recommended — Easiest & Modern)

AWS App Runner is AWS's fully managed container/app service. It provides automated build, continuous deployment, HTTPS domain (`https://*.awsapprunner.com`), and automatic scaling.

### Step 1: Push your Code to GitHub
1. Open your terminal in this project folder:
   ```bash
   cd "/Users/nikeetkumar/Carrer prediction system"
   git init
   git add .
   git commit -m "Career prediction AWS release"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```

### Step 2: Create App Runner Service in AWS Console
1. Log in to the [AWS Management Console](https://console.aws.amazon.com/).
2. In the top search bar, type **App Runner** and click it.
3. Click **Create service**.
4. Under **Source**:
   - Select **Source code repository**.
   - Connect your GitHub account and select your repository and branch (`main`).
   - Deployment trigger: Choose **Automatic** (it will redeploy whenever you push code).
5. Under **Configure build**:
   - Choose **Use a configuration file** (App Runner will automatically detect the [apprunner.yaml](file:///Users/nikeetkumar/Carrer%20prediction%20system/apprunner.yaml) already included in your project).
   - *Alternatively, if configuring manually in the console*:
     - Runtime: **Python 3**
     - Build command: `pip install -r requirements.txt`
     - Start command: `uvicorn app:app --host 0.0.0.0 --port 8000`
     - Port: `8000`
6. Under **Configure service**:
   - Service name: `career-recommendation-service`
   - Virtual CPU & Memory: `1 vCPU, 2 GB` (plenty for model inference)
7. Click **Create & deploy**.
8. In 3–5 minutes, AWS App Runner will provide your live URL with SSL:
   `https://xxxxxx.us-east-1.awsapprunner.com`

---

## 🖥️ Option 2: AWS EC2 (Free Tier with Docker)

If you prefer a dedicated virtual server under the AWS Free Tier (750 hours/month on `t2.micro` or `t3.micro`):

### Step 1: Launch an EC2 Instance
1. In the AWS Console, navigate to **EC2** -> **Instances** -> **Launch Instances**.
2. **Name**: `career-recommender-server`
3. **AMI**: `Ubuntu Server 24.04 LTS (HVM), SSD Volume Type`
4. **Instance Type**: `t2.micro` (Free tier eligible) or `t3.small` (for faster ML inference)
5. **Key pair**: Create or select an existing `.pem` key pair (e.g., `career-key.pem`).
6. **Network settings (Firewall / Security Group)**:
   - Check **Allow SSH traffic from Anywhere** (or your IP).
   - Check **Allow HTTP traffic from the internet** (Port 80).
   - Check **Allow HTTPS traffic from the internet** (Port 443).
7. Click **Launch Instance**.

### Step 2: Connect to your EC2 Instance
On your Mac terminal:
```bash
chmod 400 /path/to/career-key.pem
ssh -i /path/to/career-key.pem ubuntu@<your-ec2-public-ip>
```

### Step 3: Install Docker on the EC2 Instance
Run these commands inside your EC2 terminal:
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose git
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
newgrp docker
```

### Step 4: Deploy the App
Clone your repo and launch with Docker Compose:
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git career-system
cd career-system
docker-compose up -d --build
```

### Step 5: Access the Web App
Open your browser and visit:
```
http://<your-ec2-public-ip>
```
Your app is now live on port 80!

---

## 📦 Option 3: AWS Elastic Beanstalk

1. In the AWS Console, search for **Elastic Beanstalk** -> **Create application**.
2. **Application name**: `career-recommendation`
3. **Platform**: Choose **Docker** or **Python**.
4. **Application code**:
   - Choose **Upload your code** (zip the project folder without `__pycache__` and `.git`).
   - Or connect via the EB CLI (`eb init` and `eb deploy`).
5. Elastic Beanstalk will automatically provision the EC2 instance, security group, and domain.

---

## 🔍 Pre-Flight Checklist Before Deploying to AWS

- [x] [requirements.txt](file:///Users/nikeetkumar/Carrer%20prediction%20system/requirements.txt) includes `fastapi`, `uvicorn`, `scikit-learn`, `pandas`, `joblib`, etc.
- [x] [Dockerfile](file:///Users/nikeetkumar/Carrer%20prediction%20system/Dockerfile) is tested and configured with Python 3.11-slim.
- [x] [docker-compose.yml](file:///Users/nikeetkumar/Carrer%20prediction%20system/docker-compose.yml) binds port `80:8000` for EC2 deployment.
- [x] [apprunner.yaml](file:///Users/nikeetkumar/Carrer%20prediction%20system/apprunner.yaml) configured for zero-friction AWS App Runner deployment.
- [x] Dynamic host/port resolution and path resolution configured in [app.py](file:///Users/nikeetkumar/Carrer%20prediction%20system/app.py) and [recommendation_engine.py](file:///Users/nikeetkumar/Carrer%20prediction%20system/recommendation_engine.py).
