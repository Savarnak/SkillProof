import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class JDRequirementItem(BaseModel):
    requirement: str
    category: str
    importance: str = "high"  # high, medium
    assessed: bool = False
    evidence: str = "Not assessed"  # Strong, Demonstrated, Developing, Not assessed
    questions: List[int] = []

class JDAnalysisResult(BaseModel):
    extracted_role: str
    required_skills: List[str]
    programming_languages: List[str]
    frameworks: List[str]
    databases: List[str]
    cloud_tools: List[str]
    responsibilities: List[str]
    requirements_map: List[JDRequirementItem]

class JDAnalyzer:
    """Extracts technical skills, languages, frameworks, cloud tools, and roles from Job Descriptions."""

    SKILL_DICTIONARY = {
        "programming_languages": ["java", "python", "javascript", "typescript", "c++", "c#", "go", "sql", "html", "css", "kotlin", "swift"],
        "frameworks": ["spring boot", "spring", "react", "next.js", "angular", "node.js", "express", "django", "flask", "flutter", ".net"],
        "databases": ["postgresql", "postgres", "sql", "mysql", "mongodb", "redis", "pgvector", "dynamodb", "oracle"],
        "cloud_tools": ["aws", "azure", "gcp", "docker", "kubernetes", "git", "github", "jenkins", "terraform", "ci/cd", "rest", "microservices", "kafka", "rabbitmq"],
        "ai_emerging": ["rag", "vector databases", "llm", "llms", "generative ai", "agentic ai", "mcp", "langchain", "embeddings", "pydantic", "machine learning", "data science"]
    }

    ROLE_KEYWORDS = {
        "backend": "Backend Developer",
        "spring": "Java / Spring Boot Developer",
        "java": "Java Developer",
        "frontend": "Frontend Developer",
        "full stack": "Full Stack Developer",
        "data engineer": "Data Engineer",
        "data scientist": "Data Scientist",
        "ml": "ML Engineer",
        "ai": "AI Systems Engineer",
        "devops": "DevOps Engineer",
        "cloud": "Cloud Engineer",
        "qa": "QA / Test Engineer"
    }

    @classmethod
    def analyze_jd(cls, jd_text: str) -> JDAnalysisResult:
        jd_lower = jd_text.lower()

        # 1. Extract Role
        extracted_role = "Software Engineer"
        for kw, role_name in cls.ROLE_KEYWORDS.items():
            if kw in jd_lower:
                extracted_role = role_name
                break

        # 2. Extract Skills per Category
        found_languages = [sk.title() for sk in cls.SKILL_DICTIONARY["programming_languages"] if re.search(r'\b' + re.escape(sk) + r'\b', jd_lower)]
        found_frameworks = [sk.title() for sk in cls.SKILL_DICTIONARY["frameworks"] if re.search(r'\b' + re.escape(sk) + r'\b', jd_lower)]
        found_databases = [sk.title() for sk in cls.SKILL_DICTIONARY["databases"] if re.search(r'\b' + re.escape(sk) + r'\b', jd_lower)]
        found_cloud = [sk.title() for sk in cls.SKILL_DICTIONARY["cloud_tools"] if re.search(r'\b' + re.escape(sk) + r'\b', jd_lower)]
        found_ai = [sk.title() for sk in cls.SKILL_DICTIONARY["ai_emerging"] if re.search(r'\b' + re.escape(sk) + r'\b', jd_lower)]

        all_extracted = found_languages + found_frameworks + found_databases + found_cloud + found_ai
        if not all_extracted:
            all_extracted = ["Software Architecture", "REST APIs", "SQL", "Git"]

        # Build Requirements Map
        req_items: List[JDRequirementItem] = []
        for sk in all_extracted[:8]:  # Limit top 8 JD requirements
            req_items.append(
                JDRequirementItem(
                    requirement=sk,
                    category="Core Requirement",
                    importance="high",
                    assessed=False,
                    evidence="Not assessed",
                    questions=[]
                )
            )

        return JDAnalysisResult(
            extracted_role=extracted_role,
            required_skills=all_extracted,
            programming_languages=found_languages,
            frameworks=found_frameworks,
            databases=found_databases,
            cloud_tools=found_cloud,
            responsibilities=["Design and develop scalable production services", "Implement unit tests and system optimization"],
            requirements_map=req_items
        )

jd_analyzer = JDAnalyzer()
