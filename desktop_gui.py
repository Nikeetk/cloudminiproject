"""
Career Recommendation System - Native Desktop GUI (Tkinter)
A standalone desktop interface for career predictions, skill gap analysis,
and catalog exploration.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from recommendation_engine import CareerRecommender, CAREER_METADATA

class CareerDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Career Recommendation System")
        self.root.geometry("980x750")
        self.root.minsize(850, 650)

        # Initialize recommender engine
        try:
            self.engine = CareerRecommender()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model:\n{e}\nRun 'python3 train_model.py' first.")
            self.root.destroy()
            return

        self.setup_styles()
        self.build_ui()

    def setup_styles(self):
        self.style = ttk.Style()
        # Theme styling
        self.bg_color = "#0f172a"
        self.card_bg = "#1e293b"
        self.text_color = "#f8fafc"
        self.accent_color = "#38bdf8"
        self.accent_purple = "#818cf8"
        self.border_color = "#334155"

        self.root.configure(bg=self.bg_color)
        self.style.theme_use("clam")

        self.style.configure(".", background=self.bg_color, foreground=self.text_color, font=("Helvetica", 10))
        self.style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=self.card_bg, foreground="#94a3b8", padding=[14, 8], font=("Helvetica", 10, "bold"))
        self.style.map("TNotebook.Tab", background=[("selected", self.accent_purple)], foreground=[("selected", "#ffffff")])

        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color)
        self.style.configure("Card.TFrame", background=self.card_bg, relief="flat")
        self.style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), foreground="#38bdf8", background=self.bg_color)
        self.style.configure("SubHeader.TLabel", font=("Helvetica", 11), foreground="#94a3b8", background=self.bg_color)
        self.style.configure("Title.TLabel", font=("Helvetica", 12, "bold"), foreground="#f8fafc", background=self.card_bg)
        
        self.style.configure("Primary.TButton", font=("Helvetica", 11, "bold"), background="#6366f1", foreground="#ffffff", borderwidth=0, padding=8)
        self.style.map("Primary.TButton", background=[("active", "#4f46e5")])

        self.style.configure("Sample.TButton", font=("Helvetica", 9), background="#334155", foreground="#e2e8f0", padding=4)
        self.style.map("Sample.TButton", background=[("active", "#475569")])

    def build_ui(self):
        # Header banner
        header_frame = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=15)
        header_frame.pack(fill="x")

        tk.Label(
            header_frame,
            text="🎯 AI Career Recommendation System",
            font=("Helvetica", 18, "bold"),
            fg=self.accent_color,
            bg=self.bg_color
        ).pack(anchor="w")

        tk.Label(
            header_frame,
            text="Machine Learning Career Predictor • Skill Gap Analysis • Career Trajectory",
            font=("Helvetica", 10),
            fg="#94a3b8",
            bg=self.bg_color
        ).pack(anchor="w")

        # Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.tab_predict = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_catalog = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_stats = tk.Frame(self.notebook, bg=self.bg_color)

        self.notebook.add(self.tab_predict, text=" 🔮 Career Predictor ")
        self.notebook.add(self.tab_catalog, text=" 📚 Career Catalog ")
        self.notebook.add(self.tab_stats, text=" 📊 Model & EDA Stats ")

        self.setup_predict_tab()
        self.setup_catalog_tab()
        self.setup_stats_tab()

    def setup_predict_tab(self):
        # Main split container
        paned = tk.PanedWindow(self.tab_predict, orient="horizontal", bg=self.bg_color, sashwidth=4)
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        # Left Column: Inputs
        left_frame = tk.Frame(paned, bg=self.card_bg, padx=15, pady=15)
        paned.add(left_frame, minsize=380, width=420)

        # Right Column: Output
        right_frame = tk.Frame(paned, bg=self.card_bg, padx=15, pady=15)
        paned.add(right_frame, minsize=420)

        # Quick Load Samples Bar
        tk.Label(left_frame, text="⚡ Quick Test Profiles:", font=("Helvetica", 10, "bold"), fg="#38bdf8", bg=self.card_bg).pack(anchor="w", pady=(0, 5))
        samples_box = tk.Frame(left_frame, bg=self.card_bg)
        samples_box.pack(fill="x", pady=(0, 15))

        samples = [
            ("Data Scientist", 28, "Master's", ["Python", "Machine Learning", "Data Analysis", "SQL"], ["Data Science", "AI"]),
            ("UX Designer", 25, "Bachelor's", ["UI/UX", "Graphic Design", "Prototyping"], ["Design", "Digital Media"]),
            ("Full Stack Dev", 26, "Bachelor's", ["JavaScript", "React", "Node.js", "HTML", "CSS"], ["Web Development", "Coding"]),
            ("Cyber Analyst", 35, "Bachelor's", ["Network Security", "Linux", "Python"], ["Cybersecurity", "Technology"])
        ]

        for title, age, edu, sk, it in samples:
            btn = tk.Button(
                samples_box,
                text=title,
                font=("Helvetica", 8, "bold"),
                bg="#334155",
                fg="#ffffff",
                relief="flat",
                padx=6,
                pady=2,
                cursor="hand2",
                command=lambda a=age, e=edu, s=sk, i=it: self.load_sample(a, e, s, i)
            )
            btn.pack(side="left", padx=2, pady=2)

        # Candidate Name
        tk.Label(left_frame, text="Candidate Name / Title:", font=("Helvetica", 10), fg="#cbd5e1", bg=self.card_bg).pack(anchor="w")
        self.entry_name = tk.Entry(left_frame, font=("Helvetica", 10), bg="#0f172a", fg="#f8fafc", insertbackground="#ffffff", relief="flat")
        self.entry_name.insert(0, "Candidate")
        self.entry_name.pack(fill="x", pady=(2, 10))

        # Age and Education row
        row_age_edu = tk.Frame(left_frame, bg=self.card_bg)
        row_age_edu.pack(fill="x", pady=(0, 10))

        tk.Label(row_age_edu, text="Age:", font=("Helvetica", 10), fg="#cbd5e1", bg=self.card_bg).grid(row=0, column=0, sticky="w")
        self.spin_age = tk.Spinbox(row_age_edu, from_=18, to=70, font=("Helvetica", 10), width=6, bg="#0f172a", fg="#f8fafc", insertbackground="#ffffff")
        self.spin_age.delete(0, "end")
        self.spin_age.insert(0, 26)
        self.spin_age.grid(row=1, column=0, sticky="w", padx=(0, 15))

        tk.Label(row_age_edu, text="Education Level:", font=("Helvetica", 10), fg="#cbd5e1", bg=self.card_bg).grid(row=0, column=1, sticky="w")
        self.combo_edu = ttk.Combobox(row_age_edu, values=["Bachelor's", "Master's", "PhD"], state="readonly", font=("Helvetica", 10), width=16)
        self.combo_edu.set("Bachelor's")
        self.combo_edu.grid(row=1, column=1, sticky="w")

        # Skills Entry & Selection
        tk.Label(left_frame, text="Skills (Select or type semicolon-separated):", font=("Helvetica", 10), fg="#cbd5e1", bg=self.card_bg).pack(anchor="w")
        self.entry_skills = tk.Entry(left_frame, font=("Helvetica", 10), bg="#0f172a", fg="#f8fafc", insertbackground="#ffffff", relief="flat")
        self.entry_skills.insert(0, "Python; Machine Learning; Data Analysis")
        self.entry_skills.pack(fill="x", pady=(2, 6))

        # Skills Multi-select Listbox
        list_frame = tk.Frame(left_frame, bg=self.card_bg)
        list_frame.pack(fill="both", expand=True, pady=(0, 8))

        scroll_skills = tk.Scrollbar(list_frame)
        scroll_skills.pack(side="right", fill="y")

        self.listbox_skills = tk.Listbox(
            list_frame,
            selectmode="multiple",
            yscrollcommand=scroll_skills.set,
            font=("Helvetica", 9),
            bg="#0f172a",
            fg="#94a3b8",
            selectbackground="#6366f1",
            selectforeground="#ffffff",
            height=6,
            relief="flat"
        )
        for s in self.engine.all_skills:
            self.listbox_skills.insert("end", s)
        self.listbox_skills.pack(side="left", fill="both", expand=True)
        scroll_skills.config(command=self.listbox_skills.yview)
        self.listbox_skills.bind("<<ListboxSelect>>", self.on_skill_select)

        # Interests Entry
        tk.Label(left_frame, text="Interests (Select or type semicolon-separated):", font=("Helvetica", 10), fg="#cbd5e1", bg=self.card_bg).pack(anchor="w")
        self.entry_interests = tk.Entry(left_frame, font=("Helvetica", 10), bg="#0f172a", fg="#f8fafc", insertbackground="#ffffff", relief="flat")
        self.entry_interests.insert(0, "Technology; Data Science")
        self.entry_interests.pack(fill="x", pady=(2, 10))

        # Predict Button
        btn_predict = tk.Button(
            left_frame,
            text="✨ Predict Career Path & Skill Gap",
            font=("Helvetica", 11, "bold"),
            bg="#6366f1",
            fg="#ffffff",
            activebackground="#4f46e5",
            activeforeground="#ffffff",
            relief="flat",
            pady=8,
            cursor="hand2",
            command=self.run_prediction
        )
        btn_predict.pack(fill="x", pady=(5, 0))

        # RIGHT FRAME: Prediction Results
        tk.Label(right_frame, text="🎯 Recommendation Summary", font=("Helvetica", 14, "bold"), fg="#38bdf8", bg=self.card_bg).pack(anchor="w", pady=(0, 10))

        self.txt_result = scrolledtext.ScrolledText(
            right_frame,
            font=("Consolas", 10),
            bg="#0f172a",
            fg="#f8fafc",
            relief="flat",
            padx=10,
            pady=10
        )
        self.txt_result.pack(fill="both", expand=True)

        # Initial placeholder instructions
        self.display_welcome_text()

    def display_welcome_text(self):
        welcome = """Welcome to the AI Career Recommendation System!

Select your profile attributes on the left:
1. Enter or select your candidate details (Age & Education)
2. Pick or enter your Skills and Interests
3. Click 'Predict Career Path & Skill Gap'

Our Machine Learning engine will analyze your profile and generate:
✓ Top Recommended Career Role
✓ Calibrated Recommendation Score
✓ Industry Salary and Demand Overview
✓ Personalized Skill Gap Analysis (Matched vs. Missing Skills)
✓ Ranked Alternative Career Pathways
✓ 3-Step Actionable Learning Roadmap

Try clicking one of the 'Quick Test Profiles' at the top left to test instantly!
"""
        self.txt_result.delete("1.0", "end")
        self.txt_result.insert("1.0", welcome)

    def load_sample(self, age, edu, skills, interests):
        self.spin_age.delete(0, "end")
        self.spin_age.insert(0, age)
        self.combo_edu.set(edu)
        self.entry_skills.delete(0, "end")
        self.entry_skills.insert(0, "; ".join(skills))
        self.entry_interests.delete(0, "end")
        self.entry_interests.insert(0, "; ".join(interests))
        self.run_prediction()

    def on_skill_select(self, event):
        selected_indices = self.listbox_skills.curselection()
        selected_skills = [self.listbox_skills.get(i) for i in selected_indices]
        if selected_skills:
            self.entry_skills.delete(0, "end")
            self.entry_skills.insert(0, "; ".join(selected_skills))

    def run_prediction(self):
        try:
            age = int(self.spin_age.get())
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid numeric age.")
            return

        edu = self.combo_edu.get()
        skills_raw = self.entry_skills.get()
        interests_raw = self.entry_interests.get()

        skills = [s.strip() for s in skills_raw.split(";") if s.strip()]
        interests = [i.strip() for i in interests_raw.split(";") if i.strip()]

        if not skills:
            messagebox.showwarning("Missing Skills", "Please enter or select at least one skill.")
            return

        # Inference
        res = self.engine.recommend(age=age, education=edu, skills=skills, interests=interests)
        rec = res["recommendation"]
        gap = res["skill_gap"]
        alts = res["top_alternatives"]
        road = res["roadmap"]

        output = f"""============================================================
🎯 PRIMARY CAREER RECOMMENDATION
============================================================
Recommended Role : {rec['career']}
Match Score      : {rec['score_percent']}% ({rec['score']} score)
Domain Track     : {rec['category']}
Industry Demand  : {rec['demand']}
Salary Outlook   : {rec['salary_range']}

Overview:
{rec['description']}

Key Responsibilities:
"""
        for r in rec.get("responsibilities", []):
            output += f"  • {r}\n"

        output += f"""
============================================================
📊 SKILL GAP ANALYSIS
============================================================
Skill Match Rate : {gap['match_rate']}%

✓ SKILLS YOU POSSESS:
  {', '.join(gap['matched_skills']) if gap['matched_skills'] else 'None matched directly'}

⚠️ RECOMMENDED SKILLS TO ACQUIRE (Skill Gap):
  {', '.join(gap['missing_skills']) if gap['missing_skills'] else 'None (Fully Qualified!)'}

💡 Transferable Skills:
  {', '.join(gap['transferable_skills']) if gap['transferable_skills'] else 'None'}

============================================================
🚀 TOP ALTERNATIVE CAREER PATHS
============================================================
"""
        for i, alt in enumerate(alts, 1):
            output += f"{i}. {alt['career']} ({alt['score']}%) - Domain: {alt['category']}\n"
            output += f"   Core skills: {', '.join(alt['top_skills'])}\n"

        output += f"""
============================================================
🗺️ ACTIONABLE LEARNING ROADMAP
============================================================
"""
        for step in road:
            output += f"Step {step['step']}: {step['title']}\n"
            output += f"   {step['detail']}\n\n"

        self.txt_result.delete("1.0", "end")
        self.txt_result.insert("1.0", output)

    def setup_catalog_tab(self):
        container = tk.Frame(self.tab_catalog, bg=self.card_bg, padx=15, pady=15)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(container, text="📚 Career Directory (32 Supported Careers)", font=("Helvetica", 14, "bold"), fg="#38bdf8", bg=self.card_bg).pack(anchor="w", pady=(0, 10))

        # Career list and detail view split
        paned = tk.PanedWindow(container, orient="horizontal", bg=self.card_bg)
        paned.pack(fill="both", expand=True)

        list_box_frame = tk.Frame(paned, bg=self.card_bg)
        paned.add(list_box_frame, width=280)

        self.catalog_listbox = tk.Listbox(list_box_frame, font=("Helvetica", 10), bg="#0f172a", fg="#f8fafc", selectbackground="#6366f1")
        self.catalog_listbox.pack(fill="both", expand=True)
        for c in sorted(self.engine.career_classes):
            self.catalog_listbox.insert("end", c)
        self.catalog_listbox.bind("<<ListboxSelect>>", self.on_catalog_select)

        self.catalog_detail = scrolledtext.ScrolledText(paned, font=("Helvetica", 10), bg="#0f172a", fg="#f8fafc", relief="flat", padx=10, pady=10)
        paned.add(self.catalog_detail)

        # Select first item by default
        self.catalog_listbox.selection_set(0)
        self.on_catalog_select(None)

    def on_catalog_select(self, event):
        sel = self.catalog_listbox.curselection()
        if not sel:
            return
        career = self.catalog_listbox.get(sel[0])
        profile = self.engine.career_catalog.get(career, {})
        meta = CAREER_METADATA.get(career, {})

        details = f"""CAREER PROFILE: {career}
------------------------------------------------------------
Category:       {meta.get('category', 'General')}
Salary Range:   {meta.get('salary_range', 'Competitive')}
Industry Demand:{meta.get('demand', 'High')}
Average Score:  {profile.get('avg_score', 0.90)}
Average Age:    {profile.get('avg_age', 29)} yrs
Common Degree:  {profile.get('common_education', "Bachelor's")}

Description:
{meta.get('description', '')}

Core Required Skills:
• {', '.join(profile.get('top_skills', []))}

Key Interests:
• {', '.join(profile.get('top_interests', []))}

Daily Responsibilities:
"""
        for r in meta.get("responsibilities", []):
            details += f"• {r}\n"

        details += f"""
Recommended Certifications:
• {', '.join(meta.get('certifications', []))}

Portfolio Project Idea:
{meta.get('portfolio_project', '')}
"""
        self.catalog_detail.delete("1.0", "end")
        self.catalog_detail.insert("1.0", details)

    def setup_stats_tab(self):
        container = tk.Frame(self.tab_stats, bg=self.card_bg, padx=15, pady=15)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(container, text="📊 Dataset & Machine Learning Performance", font=("Helvetica", 14, "bold"), fg="#38bdf8", bg=self.card_bg).pack(anchor="w", pady=(0, 10))

        stats = self.engine.get_eda_stats()
        m = stats["model_metrics"]

        txt = scrolledtext.ScrolledText(container, font=("Consolas", 10), bg="#0f172a", fg="#f8fafc", relief="flat", padx=10, pady=10)
        txt.pack(fill="both", expand=True)

        report = f"""============================================================
📈 MACHINE LEARNING MODEL BENCHMARKS (Random Forest)
============================================================
Algorithm:               Random Forest Classifier (180 trees) + Gradient Boosting Regressor
Dataset Size:            {m['total_samples']} candidates
Target Classes:          {m['total_careers']} unique career designations
Test Set Size:           {m['test_size']} samples (20% holdout)

Accuracy Metrics:
• Top-1 Exact Accuracy : {m['top1_acc']}%
• Top-3 Ranked Accuracy: {m['top3_acc']}%
• Top-5 Ranked Accuracy: {m['top5_acc']}%

============================================================
📋 DATASET EDA HIGHLIGHTS
============================================================
Total Candidates:        {stats['total_candidates']}
Average Age:             {stats['avg_age']} years
Mean Recommendation Score: {stats['avg_score']}

Education Distribution:
"""
        for edu, count in stats["education_distribution"].items():
            report += f"  • {edu:15s}: {count:3d} candidates\n"

        report += "\nTop Careers by Frequency in Dataset:\n"
        for c, count in stats["career_distribution"].items():
            report += f"  • {c:28s}: {count:2d} candidates\n"

        report += "\nMost In-Demand Skills in Dataset:\n"
        for s, count in stats["top_skills"].items():
            report += f"  • {s:25s}: {count:2d} mentions\n"

        txt.insert("1.0", report)

if __name__ == "__main__":
    root = tk.Tk()
    app = CareerDesktopApp(root)
    root.mainloop()
