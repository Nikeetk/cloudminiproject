"""
Career Recommendation System - Model Training Script
Trains ML models on the career recommendation dataset, computes evaluation metrics,
and exports the model artifacts for both Web and Desktop GUIs.
"""

import json
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer, StandardScaler
from scipy.sparse import hstack, csr_matrix

def train_and_export():
    dataset_path = "AI-based Career Recommendation System.csv"
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    print(f"Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)
    print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns.")

    # 1. Clean and parse skills & interests
    def parse_semicolon(val):
        if pd.isna(val):
            return []
        return [item.strip() for item in str(val).split(";") if item.strip()]

    df["Skills_List"] = df["Skills"].apply(parse_semicolon)
    df["Interests_List"] = df["Interests"].apply(parse_semicolon)

    all_unique_skills = sorted(list(set(skill for sublist in df["Skills_List"] for skill in sublist)))
    all_unique_interests = sorted(list(set(interest for sublist in df["Interests_List"] for interest in sublist)))

    print(f"Unique skills identified: {len(all_unique_skills)}")
    print(f"Unique interests identified: {len(all_unique_interests)}")

    # 2. Multi-label binarizer for exact skill & interest matching
    mlb_skills = MultiLabelBinarizer(classes=all_unique_skills)
    skills_matrix = mlb_skills.fit_transform(df["Skills_List"])

    mlb_interests = MultiLabelBinarizer(classes=all_unique_interests)
    interests_matrix = mlb_interests.fit_transform(df["Interests_List"])

    # 3. Education encoding
    edu_encoder = LabelEncoder()
    edu_encoded = edu_encoder.fit_transform(df["Education"]).reshape(-1, 1)

    # 4. Age scaling
    age_scaler = StandardScaler()
    age_scaled = age_scaler.fit_transform(df[["Age"]])

    # 5. Combined feature matrix for Classifier
    X = np.hstack([age_scaled, edu_encoded, skills_matrix, interests_matrix])

    # 6. Target encoding
    target_encoder = LabelEncoder()
    y = target_encoder.fit_transform(df["Recommended_Career"])
    career_classes = list(target_encoder.classes_)

    # 7. Train-Test split for model evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    clf = RandomForestClassifier(
        n_estimators=150,
        max_depth=None,
        min_samples_split=2,
        random_state=42
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)

    top1_acc = accuracy_score(y_test, y_pred)
    top3_acc = sum(y_test[i] in np.argsort(y_proba[i])[-3:] for i in range(len(y_test))) / len(y_test)
    top5_acc = sum(y_test[i] in np.argsort(y_proba[i])[-5:] for i in range(len(y_test))) / len(y_test)

    print(f"Random Forest Top-1 Accuracy: {top1_acc * 100:.2f}%")
    print(f"Random Forest Top-3 Accuracy: {top3_acc * 100:.2f}%")
    print(f"Random Forest Top-5 Accuracy: {top5_acc * 100:.2f}%")

    # Fit final classifier on entire dataset for production predictions
    final_clf = RandomForestClassifier(
        n_estimators=180,
        random_state=42
    )
    final_clf.fit(X, y)

    # 8. Recommendation Score Regressor
    # Predict the recommendation score (0.80 - 0.99)
    y_scores = df["Recommendation_Score"].values
    score_regressor = GradientBoostingRegressor(n_estimators=100, random_state=42)
    score_regressor.fit(X, y_scores)

    # 9. Build career profile archetypes for Content-Based Matching & Gap Analysis
    career_catalog = {}
    for career, group in df.groupby("Recommended_Career"):
        group_skills = [s for sublist in group["Skills_List"] for s in sublist]
        group_interests = [s for sublist in group["Interests_List"] for s in sublist]
        
        skill_counts = pd.Series(group_skills).value_counts().to_dict()
        interest_counts = pd.Series(group_interests).value_counts().to_dict()
        
        career_catalog[career] = {
            "name": career,
            "sample_count": len(group),
            "avg_age": round(float(group["Age"].mean()), 1),
            "common_education": group["Education"].mode()[0] if not group["Education"].empty else "Bachelor's",
            "education_distribution": group["Education"].value_counts().to_dict(),
            "avg_score": round(float(group["Recommendation_Score"].mean()), 2),
            "required_skills": list(skill_counts.keys()),
            "top_skills": list(skill_counts.keys())[:5],
            "top_interests": list(interest_counts.keys())[:4],
        }

    # 10. Confusion Matrix for Dashboard
    cm = confusion_matrix(y_test, y_pred)

    # Save artifacts
    artifacts = {
        "classifier": final_clf,
        "score_regressor": score_regressor,
        "mlb_skills": mlb_skills,
        "mlb_interests": mlb_interests,
        "edu_encoder": edu_encoder,
        "age_scaler": age_scaler,
        "target_encoder": target_encoder,
        "all_skills": all_unique_skills,
        "all_interests": all_unique_interests,
        "career_classes": career_classes,
        "career_catalog": career_catalog,
        "metrics": {
            "top1_acc": round(top1_acc * 100, 2),
            "top3_acc": round(top3_acc * 100, 2),
            "top5_acc": round(top5_acc * 100, 2),
            "total_samples": len(df),
            "total_careers": len(career_classes),
            "test_size": len(y_test),
        }
    }

    joblib.dump(artifacts, "career_model.joblib")
    print("Exported trained model artifacts to career_model.joblib")

    # Also export JSON metadata for fast API inspection & stats
    metadata = {
        "all_skills": all_unique_skills,
        "all_interests": all_unique_interests,
        "career_classes": career_classes,
        "career_catalog": career_catalog,
        "metrics": artifacts["metrics"]
    }
    with open("career_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print("Exported metadata to career_metadata.json")

if __name__ == "__main__":
    train_and_export()
