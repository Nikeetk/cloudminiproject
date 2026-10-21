"""
Career Recommendation Engine
Provides machine learning inference, career similarity ranking, skill gap analysis,
resume text skill extraction, and dataset analytics.
"""

import os
import re
import joblib
import numpy as np
import pandas as pd

# Detailed career catalog metadata
CAREER_METADATA = {
    "AI Researcher": {
        "category": "Artificial Intelligence & Research",
        "description": "Conducts foundational and applied research into novel machine learning algorithms, deep architectures, and cognitive systems.",
        "salary_range": "$130,000 - $190,000 / yr",
        "demand": "Very High (Top Tier)",
        "responsibilities": [
            "Formulate novel hypotheses and design novel neural network architectures",
            "Publish findings in peer-reviewed AI venues (NeurIPS, ICML, CVPR)",
            "Collaborate with engineering teams to productionize breakthroughs",
            "Benchmark models against state-of-the-art benchmarks"
        ],
        "certifications": ["DeepLearning.AI TensorFlow Developer", "AWS Machine Learning Specialty"],
        "portfolio_project": "Reproduce a recent NeurIPS paper and open-source a benchmark with ablations."
    },
    "AI Specialist": {
        "category": "Artificial Intelligence & Research",
        "description": "Applies artificial intelligence and machine learning models to solve enterprise and healthcare domain challenges.",
        "salary_range": "$120,000 - $175,000 / yr",
        "demand": "High Demand",
        "responsibilities": [
            "Fine-tune pre-trained models for domain-specific tasks",
            "Evaluate model bias, safety, and operational efficiency",
            "Integrate ML inference pipelines into production cloud infrastructure"
        ],
        "certifications": ["Google Cloud Professional Machine Learning Engineer", "Azure AI Engineer"],
        "portfolio_project": "Build an AI-powered diagnostic or recommendation assistant with API endpoints."
    },
    "Automation Engineer": {
        "category": "Systems & Automation",
        "description": "Designs and implements automated test frameworks, robotics pipelines, and continuous integration workflows.",
        "salary_range": "$95,000 - $145,000 / yr",
        "demand": "Steady Growth",
        "responsibilities": [
            "Build automated CI/CD and hardware-in-the-loop testing pipelines",
            "Automate repetitive manual business operations and data ingestion",
            "Monitor automation telemetry and optimize throughput"
        ],
        "certifications": ["Certified Jenkins Engineer", "UiPath RPA Certified"],
        "portfolio_project": "End-to-end automated testing suite with synthetic test data generators and Slack alerts."
    },
    "Backend Developer": {
        "category": "Software Engineering",
        "description": "Engineers high-throughput server-side applications, microservices, databases, and resilient APIs.",
        "salary_range": "$105,000 - $160,000 / yr",
        "demand": "Very High",
        "responsibilities": [
            "Design scalable REST and gRPC API microservices",
            "Optimize database schema, indexes, and caching strategies (Redis)",
            "Ensure high availability, low latency, and robust error handling"
        ],
        "certifications": ["Oracle Certified Java Associate / Spring Professional", "AWS Certified Developer"],
        "portfolio_project": "High-concurrency microservice with Spring Boot / Go, Kafka messaging, and PostgreSQL."
    },
    "Biostatistician": {
        "category": "Data Science & Healthcare",
        "description": "Applies statistical theory to biological, pharmaceutical, and clinical trial research data.",
        "salary_range": "$100,000 - $155,000 / yr",
        "demand": "High",
        "responsibilities": [
            "Design sample size and statistical protocols for clinical trials",
            "Perform survival analysis and epidemiological modeling using R/Python",
            "Prepare statistical summary reports for regulatory compliance (FDA/EMA)"
        ],
        "certifications": ["SAS Certified Advanced Programmer", "Professional Statistician (PStat)"],
        "portfolio_project": "Survival analysis on clinical cohort survival data with interactive R Shiny / Streamlit dashboard."
    },
    "Business Analyst": {
        "category": "Business & Strategy",
        "description": "Translates complex business challenges into actionable analytical requirements, data models, and executive insights.",
        "salary_range": "$85,000 - $130,000 / yr",
        "demand": "High Demand",
        "responsibilities": [
            "Elicit and document stakeholder requirements and KPI frameworks",
            "Query data warehouses using SQL to detect operational bottlenecks",
            "Build executive reporting dashboards and forecast financial impact"
        ],
        "certifications": ["ECBA / CBAP (IIBA)", "Tableau Desktop Specialist"],
        "portfolio_project": "End-to-end customer churn analysis and financial ROI model with interactive dashboard."
    },
    "Cloud Engineer": {
        "category": "Cloud & Infrastructure",
        "description": "Architects, deploys, and maintains cloud computing environments, serverless infrastructure, and cloud security.",
        "salary_range": "$115,000 - $170,000 / yr",
        "demand": "Surging (Top 5)",
        "responsibilities": [
            "Provision Infrastructure as Code using Terraform or CloudFormation",
            "Configure virtual networks, VPC peering, and identity access management",
            "Optimize cloud compute costs and ensure 99.99% uptime"
        ],
        "certifications": ["AWS Solutions Architect Associate", "Google Cloud Associate Cloud Engineer"],
        "portfolio_project": "Multi-region resilient web infrastructure deployed with Terraform, load balanced with auto-scaling."
    },
    "Content Strategist": {
        "category": "Marketing & Media",
        "description": "Plans, creates, and governs impactful omnichannel content to captivate audiences and drive brand conversion.",
        "salary_range": "$75,000 - $120,000 / yr",
        "demand": "Steady Growth",
        "responsibilities": [
            "Develop comprehensive editorial calendars and brand tone guidelines",
            "Perform keyword research and content gap audits",
            "Analyze audience engagement metrics to refine storytelling approaches"
        ],
        "certifications": ["HubSpot Content Marketing Certification", "Google Analytics 4 Certification"],
        "portfolio_project": "360-degree brand positioning campaign with editorial guidelines and SEO performance audit."
    },
    "Cybersecurity Analyst": {
        "category": "Security & Defense",
        "description": "Monitors networks for malicious activity, executes threat hunting, and defends organizational assets.",
        "salary_range": "$100,000 - $155,000 / yr",
        "demand": "Critical / Surging",
        "responsibilities": [
            "Analyze security telemetry and SIEM logs for intrusion signals",
            "Conduct vulnerability scans and coordinate incident response protocols",
            "Enforce security best practices across Linux and enterprise endpoints"
        ],
        "certifications": ["CompTIA Security+", "Certified Ethical Hacker (CEH)"],
        "portfolio_project": "Home-lab SOC setup with Suricata IDS, Wazuh SIEM, and automated brute-force defense scripts."
    },
    "Cybersecurity Specialist": {
        "category": "Security & Defense",
        "description": "Engineers secure software architectures, cryptographic protocols, and hardening policies.",
        "salary_range": "$115,000 - $175,000 / yr",
        "demand": "Critical",
        "responsibilities": [
            "Perform penetration testing and code security audits",
            "Architect zero-trust network boundaries and identity verification",
            "Develop incident mitigation automation tools in Python/Go"
        ],
        "certifications": ["CISSP", "OSCP (Offensive Security Certified Professional)"],
        "portfolio_project": "Custom vulnerability scanner tool and security hardening audit script for Linux servers."
    },
    "Data Analyst": {
        "category": "Data Science & Analytics",
        "description": "Extracts, transforms, and analyzes structured data to uncover trends and guide strategic business choices.",
        "salary_range": "$80,000 - $125,000 / yr",
        "demand": "High Demand",
        "responsibilities": [
            "Write complex SQL queries, window functions, and aggregations",
            "Build interactive dashboards in PowerBI, Tableau, or Metabase",
            "Clean and validate raw transactional datasets for business consumption"
        ],
        "certifications": ["Google Data Analytics Professional Certificate", "Microsoft Power BI Data Analyst (PL-300)"],
        "portfolio_project": "Comprehensive E-commerce sales analytics dashboard with cohort analysis and revenue forecasting."
    },
    "Data Engineer": {
        "category": "Data Science & Infrastructure",
        "description": "Constructs reliable data pipelines, distributed storage, and real-time streaming architectures.",
        "salary_range": "$115,000 - $170,000 / yr",
        "demand": "Surging",
        "responsibilities": [
            "Design and schedule ETL/ELT pipelines using Airflow or dbt",
            "Manage distributed databases, BigQuery, Snowflake, and Apache Spark",
            "Implement data governance, schema validation, and lineage tracking"
        ],
        "certifications": ["Databricks Certified Data Engineer", "Google Cloud Professional Data Engineer"],
        "portfolio_project": "Real-time streaming pipeline reading Kafka topics, processing with PySpark, and loading into Snowflake."
    },
    "Data Scientist": {
        "category": "Data Science & AI",
        "description": "Extracts predictive value from complex datasets utilizing statistical modeling, NLP, and machine learning.",
        "salary_range": "$115,000 - $170,000 / yr",
        "demand": "Very High",
        "responsibilities": [
            "Explore unstructured and structured datasets to uncover predictive signals",
            "Develop, cross-validate, and tune machine learning models",
            "Present data stories and statistical findings to executive leaders"
        ],
        "certifications": ["IBM Data Science Professional", "DeepLearning.AI Machine Learning Specialization"],
        "portfolio_project": "End-to-end machine learning project with exploratory analysis, feature engineering, and model deployment."
    },
    "Deep Learning Engineer": {
        "category": "Artificial Intelligence & Research",
        "description": "Builds and trains advanced neural network models for computer vision, audio synthesis, and generative AI.",
        "salary_range": "$135,000 - $195,000 / yr",
        "demand": "Very High",
        "responsibilities": [
            "Implement deep architectures with PyTorch and TensorFlow",
            "Accelerate training with distributed multi-GPU / TPU pipelines",
            "Quantize and optimize models for low-latency inference (TensorRT, ONNX)"
        ],
        "certifications": ["DeepLearning.AI Deep Learning Specialization", "NVIDIA Deep Learning Institute"],
        "portfolio_project": "Vision Transformer (ViT) implementation trained on custom dataset with ONNX runtime export."
    },
    "DevOps Engineer": {
        "category": "Cloud & Infrastructure",
        "description": "Bridges software engineering and IT operations through automated delivery, monitoring, and infrastructure as code.",
        "salary_range": "$110,000 - $165,000 / yr",
        "demand": "Surging",
        "responsibilities": [
            "Build automated CI/CD pipelines with GitHub Actions / GitLab CI",
            "Manage container orchestration with Kubernetes and Docker",
            "Implement observability, Prometheus metrics, and distributed tracing"
        ],
        "certifications": ["Certified Kubernetes Administrator (CKA)", "AWS Certified DevOps Engineer"],
        "portfolio_project": "GitOps automated deployment pipeline deploying microservices to a local/cloud Kubernetes cluster."
    },
    "Digital Marketer": {
        "category": "Marketing & Media",
        "description": "Executes data-driven customer acquisition campaigns across search, social media, email, and content channels.",
        "salary_range": "$70,000 - $115,000 / yr",
        "demand": "High Demand",
        "responsibilities": [
            "Run performance marketing and paid acquisition campaigns (PPC)",
            "Perform search engine optimization (SEO) audits and link building",
            "Track conversion funnels and ROAS across multi-touch attribution"
        ],
        "certifications": ["Meta Certified Digital Marketing Associate", "Google Ads Certification"],
        "portfolio_project": "Complete SEO audit and growth marketing campaign report with CAC/LTV payback model."
    },
    "Embedded Systems Engineer": {
        "category": "Hardware & Embedded Systems",
        "description": "Programs microcontrollers, firmware, and low-level software that power IoT devices and automotive systems.",
        "salary_range": "$105,000 - $160,000 / yr",
        "demand": "High",
        "responsibilities": [
            "Write memory-efficient C and C++ firmware for ARM/RISC-V microcontrollers",
            "Debug hardware communication protocols (I2C, SPI, UART, CAN)",
            "Interface with sensors, actuators, and wireless IoT modules"
        ],
        "certifications": ["Arm System-on-Chip Design Certification", "Embedded Linux Development"],
        "portfolio_project": "IoT sensor telemetry node running FreeRTOS with low-power sleep modes and MQTT reporting."
    },
    "Financial Analyst": {
        "category": "Finance & Analytics",
        "description": "Evaluates financial health, builds DCF valuation models, and analyzes macroeconomic metrics for investments.",
        "salary_range": "$85,000 - $135,000 / yr",
        "demand": "High Demand",
        "responsibilities": [
            "Build discounted cash flow (DCF) and three-statement financial models",
            "Perform variance analysis and financial forecasting for budgeting",
            "Automate quantitative data modeling using Excel, Python, and SQL"
        ],
        "certifications": ["CFA Level 1 / 2", "Financial Modeling & Valuation Analyst (FMVA)"],
        "portfolio_project": "Public equity valuation model with Monte Carlo simulation and interactive scenario toggle."
    },
    "Front-end Developer": {
        "category": "Software Engineering & UI",
        "description": "Constructs intuitive, responsive, and accessible client-side web interfaces that delight end-users.",
        "salary_range": "$90,000 - $145,000 / yr",
        "demand": "Very High",
        "responsibilities": [
            "Build reactive web components using modern JavaScript, HTML5, and CSS",
            "Ensure cross-browser compatibility, WCAG accessibility, and web performance",
            "Integrate frontend components with REST and GraphQL backend services"
        ],
        "certifications": ["Meta Front-End Developer Professional Certificate"],
        "portfolio_project": "High-performance responsive web dashboard featuring fluid micro-animations and offline caching."
    },
    "Full Stack Developer": {
        "category": "Software Engineering",
        "description": "Develops complete software systems from responsive client-side interfaces to resilient backend APIs and databases.",
        "salary_range": "$105,000 - $165,000 / yr",
        "demand": "Very High",
        "responsibilities": [
            "Architect end-to-end features spanning React frontend and Node/Python backend",
            "Design normalized relational and document database schemas",
            "Deploy and monitor containerized applications in cloud environments"
        ],
        "certifications": ["Meta Full-Stack Developer Certificate", "AWS Certified Cloud Practitioner"],
        "portfolio_project": "Full-stack SaaS application with authentication, Stripe payment processing, and real-time sockets."
    },
    "Graphic Designer": {
        "category": "Creative Arts & Design",
        "description": "Creates compelling visual identities, brand assets, vector illustrations, and digital marketing graphics.",
        "salary_range": "$65,000 - $105,000 / yr",
        "demand": "Steady Growth",
        "responsibilities": [
            "Develop comprehensive brand visual guidelines and style palettes",
            "Craft vector illustrations, typography systems, and digital promotional collateral",
            "Collaborate with marketing teams to maintain visual brand consistency"
        ],
        "certifications": ["Adobe Certified Professional (Illustrator & Photoshop)"],
        "portfolio_project": "Complete visual rebrand case study featuring logo system, 3D assets, packaging, and digital collateral."
    },
    "Machine Learning Engineer": {
        "category": "Artificial Intelligence & Engineering",
        "description": "Deploys, monitors, and optimizes scalable machine learning models into high-volume production systems.",
        "salary_range": "$125,000 - $185,000 / yr",
        "demand": "Very High (Top 3)",
        "responsibilities": [
            "Build MLOps pipelines for automated model training, validation, and registry",
            "Deploy low-latency inference microservices using FastAPI, Triton, or TorchServe",
            "Monitor production models for data drift, concept drift, and latency degradation"
        ],
        "certifications": ["AWS Certified Machine Learning - Specialty", "GCP Professional ML Engineer"],
        "portfolio_project": "End-to-end MLOps pipeline with CI/CD model retraining, drift monitoring, and Docker deployment."
    },
    "Marketing Manager": {
        "category": "Marketing & Management",
        "description": "Directs market strategy, brand positioning, customer acquisition teams, and marketing budgets.",
        "salary_range": "$100,000 - $155,000 / yr",
        "demand": "High Demand",
        "responsibilities": [
            "Define comprehensive go-to-market strategies for product releases",
            "Manage marketing team budgets, agency partnerships, and campaign schedules",
            "Analyze customer lifecycle journeys and optimize multi-channel conversions"
        ],
        "certifications": ["Certified Product Marketing Manager (AIPMM)", "HubSpot Inbound Marketing"],
        "portfolio_project": "Go-to-market launch strategy for a B2B SaaS product with pipeline targets and attribution metrics."
    },
    "Mobile Developer": {
        "category": "Software Engineering & Mobile",
        "description": "Engineers native and cross-platform mobile experiences for iOS and Android smartphones and tablets.",
        "salary_range": "$95,000 - $150,000 / yr",
        "demand": "High Demand",
        "responsibilities": [
            "Build smooth, responsive mobile interfaces with Kotlin, Swift, or Flutter/React Native",
            "Implement offline storage, push notifications, and background location services",
            "Manage App Store and Google Play release pipelines and crash telemetry"
        ],
        "certifications": ["Google Associate Android Developer", "Meta React Native Specialization"],
        "portfolio_project": "Cross-platform mobile application with biometric login, offline SQLite synchronization, and camera integration."
    },
    "NLP Engineer": {
        "category": "Artificial Intelligence & Language",
        "description": "Builds language models, semantic search engines, conversational agents, and text classification systems.",
        "salary_range": "$125,000 - $185,000 / yr",
        "demand": "Surging (Generative AI)",
        "responsibilities": [
            "Fine-tune Large Language Models (LLMs) with LoRA/QLoRA on specialized domains",
            "Build retrieval-augmented generation (RAG) pipelines with vector databases",
            "Evaluate perplexity, hallucination rates, and semantic relevance"
        ],
        "certifications": ["Hugging Face NLP Specialist", "DeepLearning.AI NLP Specialization"],
        "portfolio_project": "Enterprise RAG assistant using LangChain/LlamaIndex, vector indexing, and custom reranker."
    },
    "Project Manager": {
        "category": "Business & Management",
        "description": "Guides cross-functional teams to deliver complex technical projects on schedule, within scope, and under budget.",
        "salary_range": "$95,000 - $145,000 / yr",
        "demand": "High Demand",
        "responsibilities": [
            "Facilitate sprint planning, daily standups, and retrospective meetings",
            "Identify cross-team dependencies, mitigate risks, and manage stakeholder expectations",
            "Track project velocity, budget burn-down, and deliver milestone deliverables"
        ],
        "certifications": ["PMP (Project Management Professional)", "Certified ScrumMaster (CSM)"],
        "portfolio_project": "Agile transformation case study managing a 6-month product migration with risk matrix and Jira metrics."
    },
    "Research Analyst": {
        "category": "Research & Strategy",
        "description": "Performs secondary and primary market research, quantitative analysis, and synthesis of industry trends.",
        "salary_range": "$80,000 - $120,000 / yr",
        "demand": "Steady Growth",
        "responsibilities": [
            "Synthesize qualitative interviews and quantitative industry datasets",
            "Forecast market sizing (TAM/SAM/SOM) and competitive landscape positioning",
            "Draft analytical briefings and presentation decks for executive leadership"
        ],
        "certifications": ["Market Research Society (MRS) Advanced Certificate"],
        "portfolio_project": "Deep-dive competitive market landscape study with quantitative forecasting and strategic recommendation deck."
    },
    "Research Scientist": {
        "category": "Research & Science",
        "description": "Directs experimental research programs, advances academic boundaries, and designs scientific methodologies.",
        "salary_range": "$115,000 - $175,000 / yr",
        "demand": "High",
        "responsibilities": [
            "Design rigorous experimental controls, statistical protocols, and data collection systems",
            "Write grant proposals and lead scientific publications",
            "Mentor doctoral fellows and present findings at international conferences"
        ],
        "certifications": ["PhD / Postdoctoral Credentials", "NIH / NSF Principal Investigator certification"],
        "portfolio_project": "Comprehensive scientific research paper with reproducible codebase and open benchmark."
    },
    "Software Developer": {
        "category": "Software Engineering",
        "description": "Builds robust software applications, core business logic, algorithmic engines, and desktop systems.",
        "salary_range": "$95,000 - $150,000 / yr",
        "demand": "Very High",
        "responsibilities": [
            "Develop clean, modular, maintainable code following SOLID principles",
            "Implement efficient data structures and algorithms for performance",
            "Write comprehensive unit and integration tests"
        ],
        "certifications": ["Microsoft Certified: Azure Developer Associate", "Oracle Certified Professional"],
        "portfolio_project": "Desktop / Web application with algorithmic pathfinding, clean MVC architecture, and unit test coverage."
    },
    "Software Engineer": {
        "category": "Software Engineering & Architecture",
        "description": "Architects resilient large-scale software systems, distributed services, and high-performance infrastructure.",
        "salary_range": "$110,000 - $170,000 / yr",
        "demand": "Surging",
        "responsibilities": [
            "Architect fault-tolerant distributed system topologies",
            "Conduct technical design reviews and establish engineering standards",
            "Optimize memory, CPU, and network bottlenecks across system components"
        ],
        "certifications": ["AWS Certified Solutions Architect", "Google Cloud Professional Cloud Architect"],
        "portfolio_project": "Distributed key-value store or rate-limiter with consensus protocol and stress benchmarks."
    },
    "UX Designer": {
        "category": "Product & Design",
        "description": "Crafts seamless user journeys, intuitive wireframes, interactive prototypes, and design systems.",
        "salary_range": "$90,000 - $145,000 / yr",
        "demand": "High Demand",
        "responsibilities": [
            "Create low-to-high fidelity wireframes, user flow diagrams, and prototypes in Figma",
            "Establish consistent design tokens and reusable design system component libraries",
            "Conduct usability testing sessions and iterate based on quantitative feedback"
        ],
        "certifications": ["Google UX Design Professional Certificate", "Nielsen Norman Group UX Master Certified"],
        "portfolio_project": "Comprehensive UX redesign case study with user journey maps, wireframes, and tested clickable prototype."
    },
    "UX Researcher": {
        "category": "Product & Design",
        "description": "Investigates user behaviors, needs, and motivations through qualitative interviews, usability tests, and telemetry.",
        "salary_range": "$95,000 - $145,000 / yr",
        "demand": "High Demand",
        "responsibilities": [
            "Conduct 1-on-1 qualitative user interviews and contextual inquiries",
            "Design and analyze survey instruments and card-sorting exercises",
            "Synthesize qualitative findings into affinity maps and actionable product recommendations"
        ],
        "certifications": ["UXQB Certified Professional for Usability and User Experience"],
        "portfolio_project": "Generative user research study on digital workflows with persona archetypes and product opportunities."
    }
}

class CareerRecommender:
    def __init__(self, model_path="career_model.joblib", dataset_path="AI-based Career Recommendation System.csv"):
        base_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
        if not os.path.exists(model_path) and os.path.exists(os.path.join(base_dir, model_path)):
            model_path = os.path.join(base_dir, model_path)
        if not os.path.exists(dataset_path) and os.path.exists(os.path.join(base_dir, dataset_path)):
            dataset_path = os.path.join(base_dir, dataset_path)

        self.artifacts = joblib.load(model_path)
        self.clf = self.artifacts["classifier"]
        self.score_regressor = self.artifacts["score_regressor"]
        self.mlb_skills = self.artifacts["mlb_skills"]
        self.mlb_interests = self.artifacts["mlb_interests"]
        self.edu_encoder = self.artifacts["edu_encoder"]
        self.age_scaler = self.artifacts["age_scaler"]
        self.target_encoder = self.artifacts["target_encoder"]
        self.career_catalog = self.artifacts["career_catalog"]
        self.all_skills = self.artifacts["all_skills"]
        self.all_interests = self.artifacts["all_interests"]
        self.career_classes = self.artifacts["career_classes"]
        self.metrics = self.artifacts["metrics"]
        self.dataset_path = dataset_path

    def recommend(self, age: int, education: str, skills: list, interests: list):
        """
        Produce primary career prediction, calibrated recommendation score,
        top alternative careers, skill gap analysis, and learning roadmap.
        """
        # Normalize and filter skills & interests
        skills_clean = [s.strip() for s in skills if s.strip()]
        interests_clean = [i.strip() for i in interests if i.strip()]

        # 1. Feature Encoding
        age_df = pd.DataFrame([[age]], columns=["Age"])
        age_scaled = self.age_scaler.transform(age_df)
        
        # Safe education encoding
        try:
            edu_encoded = self.edu_encoder.transform([education]).reshape(1, -1)
        except Exception:
            edu_encoded = np.array([[0]])

        skills_vec = self.mlb_skills.transform([skills_clean])
        interests_vec = self.mlb_interests.transform([interests_clean])

        X_input = np.hstack([age_scaled, edu_encoded, skills_vec, interests_vec])

        # 2. Classifier Probabilities
        probs = self.clf.predict_proba(X_input)[0]

        # 3. Content-based career similarity matching
        # Calculate overlap score for each career profile
        content_scores = {}
        candidate_skills_lower = set(s.lower() for s in skills_clean)
        candidate_interests_lower = set(i.lower() for i in interests_clean)

        for career, profile in self.career_catalog.items():
            career_skills_lower = set(s.lower() for s in profile.get("required_skills", []))
            career_interests_lower = set(i.lower() for i in profile.get("top_interests", []))

            skill_overlap = len(candidate_skills_lower & career_skills_lower)
            interest_overlap = len(candidate_interests_lower & career_interests_lower)

            # Normalized overlap
            skill_score = skill_overlap / max(1, len(career_skills_lower))
            interest_score = interest_overlap / max(1, len(career_interests_lower))

            content_scores[career] = (0.7 * skill_score) + (0.3 * interest_score)

        # 4. Hybrid score combination (Classifier Probability + Content Overlap)
        hybrid_scores = {}
        for idx, career in enumerate(self.career_classes):
            clf_prob = probs[idx]
            cont_score = content_scores.get(career, 0.0)
            hybrid_score = (0.55 * clf_prob) + (0.45 * cont_score)
            hybrid_scores[career] = hybrid_score

        # Rank careers
        ranked_careers = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)
        primary_career, primary_hybrid_score = ranked_careers[0]

        # 5. Recommendation Score prediction
        predicted_score = float(self.score_regressor.predict(X_input)[0])
        # Bound score between 0.80 and 0.98 for realistic calibrated output
        predicted_score = max(0.80, min(0.98, predicted_score))
        # Add slight boost if top skills strongly matched
        profile = self.career_catalog.get(primary_career, {})
        career_top_skills = profile.get("top_skills", [])
        matched_top = [s for s in career_top_skills if s.lower() in candidate_skills_lower]
        if len(matched_top) >= 2:
            predicted_score = min(0.97, predicted_score + 0.02)

        # 6. Top Alternative Careers
        top_alternatives = []
        for career, score in ranked_careers[1:6]:
            match_pct = round(score * 100, 1)
            # Ensure nice relative scale
            if match_pct > 95:
                match_pct = 94.0
            top_alternatives.append({
                "career": career,
                "score": match_pct,
                "category": CAREER_METADATA.get(career, {}).get("category", "General Professional"),
                "top_skills": self.career_catalog.get(career, {}).get("top_skills", [])[:3]
            })

        # 7. Skill Gap Analysis for the Primary Career
        all_career_skills = profile.get("required_skills", career_top_skills)
        matched_skills = [s for s in all_career_skills if s.lower() in candidate_skills_lower]
        missing_skills = [s for s in all_career_skills if s.lower() not in candidate_skills_lower]

        # If user entered skills that weren't in the career's strict list, also show them as transferable skills
        additional_skills = [s for s in skills_clean if s.lower() not in set(s.lower() for s in all_career_skills)]

        # 8. Learning Roadmap & Next Steps
        meta = CAREER_METADATA.get(primary_career, {})
        roadmap = [
            {
                "step": 1,
                "title": "Master Priority Skills",
                "detail": f"Focus on core competencies: {', '.join(missing_skills[:3]) if missing_skills else 'Advanced system design & optimization'}."
            },
            {
                "step": 2,
                "title": "Pursue Industry Certification",
                "detail": f"Recommended credential: {meta.get('certifications', ['Industry Standard Certification'])[0]}."
            },
            {
                "step": 3,
                "title": "Build Portfolio Project",
                "detail": meta.get("portfolio_project", "Create a production-grade open source project highlighting your skills.")
            }
        ]

        return {
            "candidate": {
                "age": age,
                "education": education,
                "skills_count": len(skills_clean),
                "interests_count": len(interests_clean)
            },
            "recommendation": {
                "career": primary_career,
                "score": round(predicted_score, 2),
                "score_percent": round(predicted_score * 100, 1),
                "category": meta.get("category", "Professional Track"),
                "description": meta.get("description", "Dynamic professional role in high demand."),
                "salary_range": meta.get("salary_range", "$90,000 - $150,000 / yr"),
                "demand": meta.get("demand", "High"),
                "responsibilities": meta.get("responsibilities", []),
                "certifications": meta.get("certifications", []),
                "portfolio_project": meta.get("portfolio_project", "")
            },
            "skill_gap": {
                "matched_skills": matched_skills,
                "missing_skills": missing_skills[:5],
                "transferable_skills": additional_skills,
                "match_rate": round((len(matched_skills) / max(1, len(all_career_skills))) * 100, 1)
            },
            "top_alternatives": top_alternatives,
            "roadmap": roadmap
        }

    def extract_skills_from_text(self, text: str):
        """
        Parses freeform text / resume / bio to identify matching skills and interests.
        """
        if not text:
            return {"skills": [], "interests": []}

        text_lower = text.lower()
        extracted_skills = []
        extracted_interests = []

        # Synonym / alias mapping
        aliases = {
            "js": "JavaScript",
            "ts": "TypeScript",
            "py": "Python",
            "ml": "Machine Learning",
            "dl": "Deep Learning",
            "ai": "AI",
            "nlp": "NLP",
            "reactjs": "React",
            "react.js": "React",
            "nodejs": "Node.js",
            "node": "Node.js",
            "k8s": "DevOps",
            "kubernetes": "DevOps",
            "docker": "DevOps",
            "postgres": "SQL",
            "postgresql": "SQL",
            "mysql": "SQL",
            "aws": "Cloud Computing",
            "azure": "Cloud Computing",
            "gcp": "Cloud Computing",
            "ux/ui": "UI/UX",
            "figma": "UI/UX",
            "photoshop": "Adobe Photoshop",
            "illustrator": "Adobe Illustrator",
            "power bi": "Data Visualization",
            "tableau": "Data Visualization",
            "agile/scrum": "Agile",
            "scrum": "Agile"
        }

        # Check aliases
        for alias, mapped_skill in aliases.items():
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, text_lower):
                if mapped_skill in self.all_skills and mapped_skill not in extracted_skills:
                    extracted_skills.append(mapped_skill)

        # Check all unique skills
        for skill in self.all_skills:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                if skill not in extracted_skills:
                    extracted_skills.append(skill)

        # Check all unique interests
        for interest in self.all_interests:
            pattern = r'\b' + re.escape(interest.lower()) + r'\b'
            if re.search(pattern, text_lower):
                if interest not in extracted_interests:
                    extracted_interests.append(interest)

        return {
            "skills": sorted(extracted_skills),
            "interests": sorted(extracted_interests)
        }

    def get_eda_stats(self):
        """
        Computes aggregate statistics for the EDA & Model Insights dashboard.
        """
        df = pd.read_csv(self.dataset_path)

        # 1. Career distribution (Top 10)
        career_counts = df["Recommended_Career"].value_counts().head(10).to_dict()

        # 2. Education distribution
        edu_counts = df["Education"].value_counts().to_dict()

        # 3. Age distribution
        age_bins = [20, 25, 30, 35, 45]
        age_labels = ["20-24", "25-29", "30-34", "35+"]
        df["Age_Group"] = pd.cut(df["Age"], bins=age_bins, labels=age_labels, right=False)
        age_counts = df["Age_Group"].value_counts().sort_index().to_dict()
        age_counts = {str(k): int(v) for k, v in age_counts.items()}

        # 4. Top skills in dataset
        all_s = []
        for item in df["Skills"].dropna():
            all_s.extend([x.strip() for x in str(item).split(";") if x.strip()])
        top_skills = pd.Series(all_s).value_counts().head(12).to_dict()

        # 5. Top interests in dataset
        all_i = []
        for item in df["Interests"].dropna():
            all_i.extend([x.strip() for x in str(item).split(";") if x.strip()])
        top_interests = pd.Series(all_i).value_counts().head(10).to_dict()

        return {
            "total_candidates": len(df),
            "total_careers": df["Recommended_Career"].nunique(),
            "avg_age": round(float(df["Age"].mean()), 1),
            "avg_score": round(float(df["Recommendation_Score"].mean()), 2),
            "career_distribution": career_counts,
            "education_distribution": edu_counts,
            "age_distribution": age_counts,
            "top_skills": top_skills,
            "top_interests": top_interests,
            "model_metrics": self.metrics
        }
