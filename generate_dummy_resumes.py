#!/usr/bin/env python3
"""Generate realistic dummy resume TXT files for testing the RAG pipeline."""

from __future__ import annotations

from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "resumes"

PROFILES: list[dict] = [
  # Backend Engineers
  {"role": "Backend Engineer", "name": "Arjun Mehta", "years": 1,
   "skills": "Python, Django, REST APIs, PostgreSQL, Git",
   "jobs": [("Junior Backend Developer", "NovaStack", "Jul 2024 - Present", "Built REST endpoints and unit tests for billing service.")],
   "edu": "B.Tech Information Technology, VIT Vellore, 2024",
   "project": "Campus Food Ordering API - Django REST service with JWT auth.",
   "certs": "Python Institute PCEP"},
  {"role": "Backend Engineer", "name": "Priya Nair", "years": 3,
   "skills": "Java, Spring Boot, MySQL, Redis, Kafka, Docker",
   "jobs": [("Backend Engineer", "FinEdge", "Mar 2023 - Present", "Designed payment microservices handling 2M daily transactions."),
            ("Associate Engineer", "CodeHarbor", "Jun 2022 - Feb 2023", "Maintained legacy monolith and migrated modules to Spring Boot.")],
   "edu": "B.E. Computer Science, PES University, 2022",
   "project": "Ledger Sync - event-driven accounting reconciliation with Kafka.",
   "certs": "Oracle Certified Professional: Java SE 11 Developer"},
  {"role": "Backend Engineer", "name": "Rohan Kapoor", "years": 6,
   "skills": "Python, FastAPI, PostgreSQL, AWS, Celery, GraphQL",
   "jobs": [("Senior Backend Engineer", "CloudRoute", "Jan 2021 - Present", "Led API platform serving 40+ internal teams."),
            ("Software Engineer", "DataPulse", "Aug 2018 - Dec 2020", "Built analytics ingestion pipelines in Python.")],
   "edu": "B.Tech Computer Science, IIT Roorkee, 2018",
   "project": "Inventory Optimizer - real-time stock API with FastAPI and Redis.",
   "certs": "AWS Certified Developer - Associate"},
  {"role": "Backend Engineer", "name": "Sneha Iyer", "years": 10,
   "skills": "Go, Python, Kubernetes, PostgreSQL, gRPC, AWS, System Design",
   "jobs": [("Staff Backend Engineer", "ShopVerse", "May 2019 - Present", "Architected order fulfillment platform across 3 regions."),
            ("Senior Engineer", "TravelMint", "Jul 2015 - Apr 2019", "Owned search and booking services at scale.")],
   "edu": "M.Tech Software Systems, BITS Pilani, 2015",
   "project": "Rate Limiter Service - distributed token bucket in Go.",
   "certs": "AWS Certified Solutions Architect - Professional"},
  {"role": "Backend Engineer", "name": "Vikram Singh", "years": 14,
   "skills": "Java, Scala, Kafka, Cassandra, AWS, Microservices, Team Leadership",
   "jobs": [("Principal Engineer", "PayGrid", "Feb 2018 - Present", "Defined platform standards for 120-engineer org."),
            ("Senior Backend Engineer", "TelcoSoft", "Jun 2011 - Jan 2018", "Built telecom billing and provisioning systems.")],
   "edu": "B.Tech Electronics and Communication, NIT Trichy, 2011",
   "project": "Multi-tenant Billing Engine - high-throughput invoice generation.",
   "certs": "AWS Certified Solutions Architect - Professional, CKA"},
  # Frontend Engineers
  {"role": "Frontend Engineer", "name": "Ananya Sharma", "years": 2,
   "skills": "JavaScript, React, TypeScript, HTML, CSS, Tailwind CSS",
   "jobs": [("Frontend Developer", "PixelCraft", "Aug 2023 - Present", "Implemented responsive dashboards for SaaS clients."),
            ("Intern", "Webloom", "Jan 2023 - Jul 2023", "Built reusable React component library.")],
   "edu": "B.Sc. Computer Science, Christ University, 2023",
   "project": "Habit Tracker UI - React app with local storage persistence.",
   "certs": ""},
  {"role": "Frontend Engineer", "name": "Karthik Reddy", "years": 4,
   "skills": "React, Next.js, TypeScript, Redux, Jest, Figma",
   "jobs": [("Frontend Engineer", "MarketHive", "Oct 2022 - Present", "Developed seller portal used by 15k merchants."),
            ("UI Developer", "BrightApps", "Jun 2021 - Sep 2022", "Converted design systems into accessible components.")],
   "edu": "B.Tech Computer Science, SRM University, 2021",
   "project": "E-commerce Storefront - Next.js SSR with Stripe checkout.",
   "certs": "Meta Front-End Developer Professional Certificate"},
  {"role": "Frontend Engineer", "name": "Meera Joshi", "years": 7,
   "skills": "React, Vue.js, TypeScript, Webpack, Performance Optimization, Accessibility",
   "jobs": [("Senior Frontend Engineer", "StreamLine", "Mar 2020 - Present", "Improved Core Web Vitals by 35% across product suite."),
            ("Frontend Developer", "AdSpark", "Jul 2018 - Feb 2020", "Built ad campaign management interfaces.")],
   "edu": "B.E. Information Technology, COEP Pune, 2018",
   "project": "Design System Kit - cross-framework component tokens and docs.",
   "certs": ""},
  {"role": "Frontend Engineer", "name": "Nikhil Desai", "years": 11,
   "skills": "React, Angular, TypeScript, Micro-frontends, Node.js, CI/CD",
   "jobs": [("Lead Frontend Engineer", "HealthBridge", "Jan 2017 - Present", "Led frontend guild and micro-frontend migration."),
            ("Senior UI Engineer", "GameForge", "May 2014 - Dec 2016", "Shipped real-time multiplayer lobby interfaces.")],
   "edu": "M.S. Human-Computer Interaction, Georgia Tech, 2014",
   "project": "Patient Portal - HIPAA-aware React SPA with role-based views.",
   "certs": "Certified Accessibility Specialist (CPACC)"},
  {"role": "Frontend Engineer", "name": "Divya Krishnan", "years": 15,
   "skills": "JavaScript, React, TypeScript, Web Performance, Architecture, Mentoring",
   "jobs": [("Principal Frontend Engineer", "GlobalCart", "Apr 2015 - Present", "Set frontend architecture for 50M MAU platform."),
            ("Senior Developer", "MediaWave", "Jun 2010 - Mar 2015", "Built video streaming player and analytics UI.")],
   "edu": "B.Tech Computer Science, Anna University, 2010",
   "project": "Universal Shell - module federation host for 12 product teams.",
   "certs": "Google Mobile Web Specialist"},
  # Data Scientists
  {"role": "Data Scientist", "name": "Aditya Banerjee", "years": 2,
   "skills": "Python, Pandas, SQL, Scikit-learn, Matplotlib, Jupyter",
   "jobs": [("Data Scientist", "Insight Labs", "Sep 2023 - Present", "Built churn models for subscription business."),
            ("Data Analyst Intern", "RetailIQ", "Jan 2023 - Aug 2023", "Automated weekly sales reporting pipelines.")],
   "edu": "M.Sc. Statistics, ISI Kolkata, 2023",
   "project": "Customer Segmentation - RFM clustering for e-commerce cohorts.",
   "certs": ""},
  {"role": "Data Scientist", "name": "Pooja Menon", "years": 5,
   "skills": "Python, SQL, XGBoost, A/B Testing, Tableau, Spark",
   "jobs": [("Data Scientist", "BankNova", "Feb 2021 - Present", "Developed credit risk models with 12% default reduction."),
            ("Analyst", "Quantify", "Jul 2019 - Jan 2021", "Ran experiment analysis for growth product team.")],
   "edu": "B.Tech Mathematics and Computing, IIT Delhi, 2019",
   "project": "Fraud Detection - gradient boosting classifier on transaction features.",
   "certs": "Google Data Analytics Professional Certificate"},
  {"role": "Data Scientist", "name": "Harish Pillai", "years": 8,
   "skills": "Python, R, SQL, Machine Learning, Time Series, AWS, Snowflake",
   "jobs": [("Senior Data Scientist", "LogiChain", "May 2018 - Present", "Forecasted demand for 200+ SKUs with 8% MAPE improvement."),
            ("Data Scientist", "AgriSense", "Aug 2016 - Apr 2018", "Built crop yield prediction models from satellite data.")],
   "edu": "M.Tech Data Science, IIIT Bangalore, 2016",
   "project": "Supply Forecast Dashboard - Prophet and XGBoost ensemble pipeline.",
   "certs": "AWS Certified Machine Learning - Specialty"},
  {"role": "Data Scientist", "name": "Lakshmi Rao", "years": 12,
   "skills": "Python, SQL, Causal Inference, Experimentation, ML Ops, Leadership",
   "jobs": [("Lead Data Scientist", "StreamFlix", "Oct 2016 - Present", "Owned recommendation experimentation framework."),
            ("Data Scientist", "AdMetrics", "Jun 2013 - Sep 2016", "Optimized ad bidding algorithms.")],
   "edu": "Ph.D. Applied Statistics, University of Michigan, 2013",
   "project": "Uplift Modeling Framework - causal ML for marketing campaigns.",
   "certs": ""},
  {"role": "Data Scientist", "name": "Suresh Varma", "years": 13,
   "skills": "Python, Spark, Bayesian Methods, NLP, Data Strategy, Stakeholder Management",
   "jobs": [("Principal Data Scientist", "InsureTech Pro", "Mar 2014 - Present", "Led pricing science team across life and health products."),
            ("Senior Scientist", "TelAnalytics", "Jul 2011 - Feb 2014", "Built network fault prediction models.")],
   "edu": "M.S. Data Science, Columbia University, 2011",
   "project": "Claims Triage Model - NLP classification of insurance requests.",
   "certs": "Databricks Certified Machine Learning Professional"},
  # ML Engineers
  {"role": "ML Engineer", "name": "Ishaan Gupta", "years": 1,
   "skills": "Python, PyTorch, Scikit-learn, Docker, Git, Linux",
   "jobs": [("ML Engineer Intern", "Visionary AI", "Jun 2024 - Present", "Fine-tuned image classifiers for defect detection.")],
   "edu": "B.Tech Artificial Intelligence, IIIT Hyderabad, 2024",
   "project": "Sentiment Classifier - BERT fine-tuning on product reviews.",
   "certs": "DeepLearning.AI TensorFlow Developer"},
  {"role": "ML Engineer", "name": "Neha Choudhary", "years": 4,
   "skills": "Python, TensorFlow, PyTorch, MLflow, Kubernetes, AWS",
   "jobs": [("ML Engineer", "AutoDrive", "Nov 2022 - Present", "Deployed perception models to edge devices."),
            ("Junior ML Engineer", "RoboWorks", "Aug 2021 - Oct 2022", "Built data labeling and training pipelines.")],
   "edu": "M.Tech Robotics, IIT Kanpur, 2021",
   "project": "Object Detection Pipeline - YOLOv8 training and ONNX export.",
   "certs": "AWS Certified Machine Learning - Specialty"},
  {"role": "ML Engineer", "name": "Rahul Verma", "years": 7,
   "skills": "Python, PyTorch, Kubeflow, Feature Stores, Ray, GCP",
   "jobs": [("Senior ML Engineer", "SearchPrime", "Jan 2020 - Present", "Productionized ranking models with sub-50ms latency."),
            ("ML Engineer", "ChatNest", "Jul 2018 - Dec 2019", "Implemented intent classification for support bot.")],
   "edu": "B.Tech Computer Science, NIT Warangal, 2018",
   "project": "Real-time Ranking Service - TensorFlow Serving on GKE.",
   "certs": "Google Professional Machine Learning Engineer"},
  {"role": "ML Engineer", "name": "Tanvi Shah", "years": 9,
   "skills": "Python, PyTorch, MLOps, Airflow, Docker, AWS, System Design",
   "jobs": [("Staff ML Engineer", "FinML Corp", "Mar 2018 - Present", "Built feature platform used by 8 model teams."),
            ("ML Engineer", "VoiceNet", "Jun 2016 - Feb 2018", "Deployed speech-to-text models for IVR systems.")],
   "edu": "M.S. Machine Learning, Carnegie Mellon University, 2016",
   "project": "Feature Store - Feast-based pipeline with online/offline serving.",
   "certs": "AWS Certified Solutions Architect - Associate"},
  {"role": "ML Engineer", "name": "Amit Patel", "years": 14,
   "skills": "Python, Distributed Training, LLMs, CUDA, Kubernetes, Technical Leadership",
   "jobs": [("Principal ML Engineer", "OpenScale AI", "Feb 2015 - Present", "Led LLM fine-tuning infrastructure for enterprise customers."),
            ("Senior ML Engineer", "Vision Systems", "May 2011 - Jan 2015", "Built GPU training clusters and model registry.")],
   "edu": "Ph.D. Computer Science, Stanford University, 2011",
   "project": "Distributed Fine-tuning Platform - multi-node LoRA training orchestrator.",
   "certs": "NVIDIA DLI Certified Instructor"},
  # DevOps Engineers
  {"role": "DevOps Engineer", "name": "Sanjay Kulkarni", "years": 3,
   "skills": "Linux, Docker, Kubernetes, Jenkins, Terraform, AWS",
   "jobs": [("DevOps Engineer", "ShipFast", "Apr 2023 - Present", "Managed CI/CD for 25 microservices."),
            ("Systems Engineer", "HostBridge", "Jul 2022 - Mar 2023", "Automated server provisioning with Ansible.")],
   "edu": "B.E. Computer Engineering, Pune University, 2022",
   "project": "GitOps Deployment - Argo CD rollout for staging and production.",
   "certs": "CKA, AWS Certified SysOps Administrator"},
  {"role": "DevOps Engineer", "name": "Deepa Nambiar", "years": 6,
   "skills": "Kubernetes, Terraform, AWS, Prometheus, Grafana, Helm",
   "jobs": [("Senior DevOps Engineer", "ScaleOps", "Oct 2020 - Present", "Reduced deployment time by 60% with pipeline redesign."),
            ("DevOps Engineer", "CloudNine", "Jun 2018 - Sep 2020", "Migrated on-prem workloads to AWS EKS.")],
   "edu": "B.Tech Information Technology, NIT Surathkal, 2018",
   "project": "Observability Stack - Prometheus, Loki, and Grafana on EKS.",
   "certs": "AWS Certified DevOps Engineer - Professional"},
  {"role": "DevOps Engineer", "name": "Manoj Eswaran", "years": 8,
   "skills": "AWS, Azure, Kubernetes, Terraform, Python, Security, SRE",
   "jobs": [("DevOps Lead", "HealthCloud", "Feb 2019 - Present", "Owned HIPAA-compliant infrastructure and incident response."),
            ("Site Reliability Engineer", "PaySwift", "Aug 2016 - Jan 2019", "Achieved 99.95% uptime for payment APIs.")],
   "edu": "B.Tech Computer Science, PSG College of Technology, 2016",
   "project": "Disaster Recovery Runbooks - automated failover for multi-AZ clusters.",
   "certs": "CKA, Azure Administrator Associate"},
  {"role": "DevOps Engineer", "name": "Kavita Bhat", "years": 10,
   "skills": "Kubernetes, Istio, Terraform, AWS, GitOps, Cost Optimization",
   "jobs": [("Staff DevOps Engineer", "RetailGrid", "May 2017 - Present", "Standardized platform engineering practices globally."),
            ("Senior SRE", "StreamBox", "Jul 2014 - Apr 2017", "Built auto-scaling video delivery infrastructure.")],
   "edu": "M.Tech Computer Networks, IIT Madras, 2014",
   "project": "Service Mesh Migration - Istio rollout with zero-downtime cutover.",
   "certs": "AWS Certified Solutions Architect - Professional, CKS"},
  {"role": "DevOps Engineer", "name": "Gopal Menon", "years": 15,
   "skills": "Cloud Architecture, Kubernetes, Terraform, Security, Leadership, FinOps",
   "jobs": [("Director of Platform Engineering", "MegaMart Online", "Jan 2014 - Present", "Built platform org supporting 300+ engineers."),
            ("Principal SRE", "TelcoCloud", "Jun 2009 - Dec 2013", "Designed national CDN and edge compute platform.")],
   "edu": "B.E. Electronics and Telecommunication, Mumbai University, 2009",
   "project": "Internal Developer Platform - self-service environments with Backstage.",
   "certs": "CKA, CKS, AWS Certified Solutions Architect - Professional"},
  # QA Engineers
  {"role": "QA Engineer", "name": "Ritu Malhotra", "years": 2,
   "skills": "Manual Testing, Selenium, Java, Test Cases, JIRA, API Testing",
   "jobs": [("QA Engineer", "AppSure", "Dec 2023 - Present", "Executed regression suites for mobile banking app."),
            ("QA Intern", "SoftNest", "Jun 2023 - Nov 2023", "Logged defects and verified fixes across sprints.")],
   "edu": "B.Sc. Computer Science, Delhi University, 2023",
   "project": "API Test Suite - Postman collections for checkout flows.",
   "certs": "ISTQB Foundation Level"},
  {"role": "QA Engineer", "name": "Varun Agarwal", "years": 5,
   "skills": "Selenium, Cypress, Python, API Testing, CI/CD, Performance Testing",
   "jobs": [("QA Automation Engineer", "EduSpark", "Mar 2022 - Present", "Built Cypress E2E suite covering 80% critical paths."),
            ("QA Analyst", "FormLogic", "Aug 2019 - Feb 2022", "Owned test planning for SaaS form builder.")],
   "edu": "B.Tech Computer Science, Jaypee Institute, 2019",
   "project": "Load Testing Framework - k6 scripts integrated in GitHub Actions.",
   "certs": "ISTQB Advanced Test Automation Engineer"},
  {"role": "QA Engineer", "name": "Shreya Dutta", "years": 7,
   "skills": "Playwright, Java, REST Assured, Jenkins, Test Strategy, Agile",
   "jobs": [("Senior QA Engineer", "TravelGo", "Jul 2019 - Present", "Led QA for booking and payments squads."),
            ("Automation Engineer", "ShopEase", "May 2017 - Jun 2019", "Automated checkout and refund workflows.")],
   "edu": "B.E. Computer Science, Jadavpur University, 2017",
   "project": "Visual Regression Tests - Playwright snapshots for design QA.",
   "certs": "Certified Scrum Master (CSM)"},
  {"role": "QA Engineer", "name": "Abhishek Roy", "years": 11,
   "skills": "Test Architecture, Selenium Grid, API Testing, Security Testing, Team Leadership",
   "jobs": [("QA Lead", "MediCore Systems", "Oct 2016 - Present", "Defined quality gates for FDA-regulated releases."),
            ("Senior QA Engineer", "FleetTrack", "Jun 2014 - Sep 2016", "Built automation for GPS fleet management platform.")],
   "edu": "M.Tech Software Engineering, BITS Pilani, 2014",
   "project": "Compliance Test Harness - traceable test evidence for audits.",
   "certs": "ISTQB Expert Level Test Management"},
  {"role": "QA Engineer", "name": "Nandini Rao", "years": 12,
   "skills": "Quality Engineering, Playwright, CI/CD, Test Strategy, Mentoring, Risk Analysis",
   "jobs": [("Principal QA Engineer", "BankSecure", "Feb 2015 - Present", "Established org-wide test automation standards."),
            ("Senior QA", "InsureFlow", "Aug 2012 - Jan 2015", "Led UAT for policy administration system.")],
   "edu": "B.Tech Electronics and Communication, RV College of Engineering, 2012",
   "project": "Shift-left Testing Program - developer-owned contract tests in CI.",
   "certs": "ISTQB Expert Level, Certified Agile Leadership"},
]


def slugify(name: str, role: str, years: int) -> str:
    role_slug = role.lower().replace(" ", "_")
    name_slug = name.lower().replace(" ", "_")
    return f"{role_slug}_{name_slug}_{years}y.txt"


def email_from_name(name: str) -> str:
    return name.lower().replace(" ", ".") + "@email.com"


def format_resume(profile: dict) -> str:
    name = profile["name"]
    lines = [
        name,
        f"{email_from_name(name)} | +91 98{profile['years']:02d} {hash(name) % 10000:04d} {hash(name + 'x') % 10000:04d}",
        "",
        "Skills",
        profile["skills"],
        "",
        "Experience",
    ]
    for title, company, dates, bullet in profile["jobs"]:
        lines.append(f"{title} | {company} | {dates}")
        lines.append(f"- {bullet}")
        lines.append("")
    lines.append("Education")
    lines.append(profile["edu"])
    lines.append("")
    lines.append("Projects")
    lines.append(profile["project"])
    if profile.get("certs"):
        lines.extend(["", "Certifications", profile["certs"]])
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for profile in PROFILES:
        filename = slugify(profile["name"], profile["role"], profile["years"])
        path = OUTPUT_DIR / filename
        path.write_text(format_resume(profile), encoding="utf-8")
    print(f"Generated {len(PROFILES)} resumes in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
