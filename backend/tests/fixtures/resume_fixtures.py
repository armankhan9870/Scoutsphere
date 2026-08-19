"""Test fixtures for ATS Analysis unit and integration testing."""

KNOWN_BAD_RESUME = """
John Smith
+---------------------------------------------------+
| Email: john@example.com | Phone: 555-0199         |
+---------------------------------------------------+

Stuff I Did

- worked on backend APIs and databases
- responsible for fixing bugs in the application
- helped with writing unit tests for software
- did some python and javascript coding when requested
"""

KNOWN_GOOD_RESUME = """
Alex Rivera
Email: alex.rivera@scoutsphere.ai | Phone: (555) 234-5678 | San Francisco, CA
LinkedIn: linkedin.com/in/alexrivera | GitHub: github.com/alexrivera

PROFESSIONAL SUMMARY
Senior AI & Systems Engineer with over 6 years of professional experience architecting high-scalability backend platforms, distributed RAG pipelines, and enterprise HR tech solutions. Proven track record in optimizing microservice performance, automating infrastructure, and deploying production LLM agents across enterprise environments. Skilled in system design, database optimization, cloud architecture, and technical leadership.

TECHNICAL SKILLS
- Languages: Python, TypeScript, SQL, Go, C++, HTML/CSS, Bash
- Frameworks & Libraries: FastAPI, React, Node.js, PyTorch, LangGraph, Pydantic, SQLAlchemy
- Databases & Infrastructure: PostgreSQL, pgvector, Redis, Docker, AWS, Kubernetes, CI/CD, Kafka, NGINX
- Core Methodologies: Agile, System Design, Microservices, Unit Testing, Code Review, Security Best Practices

WORK EXPERIENCE
Senior Backend Engineer | TechCorp Solutions | 2022 - Present
- Engineered high-throughput FastAPI microservice platform, reducing average P99 API response latency by 45% across 2.5M daily active users.
- Architected PostgreSQL query caching layer with Redis clusters, cutting overall database CPU utilization by 35% and saving $12,000 in monthly cloud infrastructure expenses.
- Spearheaded zero-downtime migration of legacy monolithic backend to containerized Kubernetes microservices, achieving 99.99% system uptime SLA and accelerating feature deployment velocity by 3x.
- Automated end-to-end CI/CD deployment pipelines using Docker, Helm, and GitHub Actions, reducing manual release cycle duration from 4 hours down to 12 minutes.
- Implemented robust rate-limiting middleware and OAuth2 token authorization services, securing public API endpoints against DDOS vectors and handling over 500 requests per second cleanly.

Software Developer | DataDriven Systems | 2019 - 2022
- Developed scalable distributed data ingestion pipeline processing over 10M daily telemetry events using Python, AsyncIO, and Apache Kafka.
- Optimized complex SQL database queries and composite B-tree indexes, decreasing API analytical search response times by 60% for high-volume enterprise clients.
- Led cross-functional team of 5 backend and frontend engineers to design and deliver real-time analytics dashboard, increasing overall user retention by 25%.
- Implemented comprehensive automated unit test suite with 92% code coverage, catching over 150 regression bugs prior to production releases.

PROJECTS & CERTIFICATIONS
ScoutSphere Enterprise Resume Parser
- Designed standalone AI-powered ATS resume screening engine using deterministic parsing algorithms combined with LLM qualitative analysis.
- AWS Certified Solutions Architect - Associate (Issued 2023)

EDUCATION
Bachelor of Science in Computer Science | Stanford University | Graduated 2019
- Honors: Magna Cum Laude, Dean's List for 6 Consecutive Semesters
"""
