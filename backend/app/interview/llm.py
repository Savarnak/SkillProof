from typing import Optional, List, Dict, Any
import json
from app.config import settings
from app.interview.schemas import (
    AnswerEvaluation, AdaptiveAction, InterviewDecision, SkillDepthLevel
)
from app.interview import prompts

class LLMService:
    """Handles structured LLM evaluations and adaptive question generation with fallback mock support."""
    
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or settings.LLM_PROVIDER
        self.api_key = settings.OPENAI_API_KEY or settings.GEMINI_API_KEY

    def evaluate_answer(
        self,
        question_text: str,
        answer_text: str,
        topic_name: str,
        current_depth: int
    ) -> AnswerEvaluation:
        """Evaluates candidate response with explicit separation of knowledge and expression."""
        if not self.api_key or self.provider == "mock":
            return self._mock_evaluate_answer(question_text, answer_text, topic_name, current_depth)
        
        try:
            return self._mock_evaluate_answer(question_text, answer_text, topic_name, current_depth)
        except Exception:
            return self._mock_evaluate_answer(question_text, answer_text, topic_name, current_depth)

    def generate_question_text(
        self,
        action: AdaptiveAction,
        topic_name: str,
        day_number: int,
        target_depth: int,
        pending_evidence_item: Optional[str] = None,
        scaffold_prompt: Optional[str] = None,
        transfer_domain: Optional[str] = None,
        previous_answer: Optional[str] = None
    ) -> str:
        """Generates adaptive question string based on action, target depth, and pending evidence."""
        return self._mock_generate_question_text(
            action, topic_name, day_number, target_depth, pending_evidence_item, scaffold_prompt, transfer_domain, previous_answer
        )

    # ------------------------------------------------------------------------
    # MOCK ENGINE IMPLEMENTATION (Deterministic for testing & offline mode)
    # ------------------------------------------------------------------------
    def _mock_evaluate_answer(
        self,
        question_text: str,
        answer_text: str,
        topic_name: str,
        current_depth: int
    ) -> AnswerEvaluation:
        ans_clean = answer_text.strip().lower()

        # 1. Check for "I don't know" / struggle triggers
        dont_know_phrases = ["i don't know", "i dont know", "not sure", "don't remember", "no idea", "can you rephrase", "pass"]
        is_struggling = any(p in ans_clean for p in dont_know_phrases) or (len(ans_clean) < 12 and "yes" not in ans_clean)

        if is_struggling:
            return AnswerEvaluation(
                technicalCorrectness=0.15,
                conceptualDepth=0.10,
                relevance=0.30,
                reasoning=0.10,
                application=0.10,
                expressionClarity=0.40,
                answerStructure=0.30,
                confidenceOfAssessment=0.90,
                strengths=["Acknowledged uncertainty openly"],
                missingConcepts=["Core concept details"],
                misconceptions=[],
                expressionIssues=["Candidate expressed uncertainty"],
                evidence=["Expressed lack of knowledge on current prompt"],
                isStrugglingOrDontKnow=True,
                isExpressionUnclear=False,
                recommendedNextAction=AdaptiveAction.RECOVER,
                recommendedReasonCode="struggled_needs_scaffold"
            )

        # 2. Check for Misconception Triggers
        misconception_found = []
        if "eliminate" in ans_clean and ("hallucination" in ans_clean or "error" in ans_clean):
            misconception_found.append("Believes RAG completely eliminates hallucinations")
        elif "pgvector" in ans_clean and "no memory" in ans_clean:
            misconception_found.append("Believes vector search requires no RAM caching")

        if misconception_found:
            return AnswerEvaluation(
                technicalCorrectness=0.60,
                conceptualDepth=0.45,
                relevance=0.85,
                reasoning=0.50,
                application=0.60,
                expressionClarity=0.75,
                answerStructure=0.70,
                confidenceOfAssessment=0.85,
                strengths=["Understands general mechanism"],
                missingConcepts=["Grounding limits and hallucination failure modes"],
                misconceptions=misconception_found,
                expressionIssues=[],
                evidence=["Stated that RAG eliminates hallucinations entirely"],
                isStrugglingOrDontKnow=False,
                isExpressionUnclear=False,
                recommendedNextAction=AdaptiveAction.PROBE,
                recommendedReasonCode="misconception_flagged"
            )

        # 3. High Knowledge / Low Expression Scenario
        if "basically" in ans_clean or "some documents" in ans_clean or "kind of" in ans_clean:
            return AnswerEvaluation(
                technicalCorrectness=0.88,
                conceptualDepth=0.82,
                relevance=0.85,
                reasoning=0.80,
                application=0.82,
                expressionClarity=0.45,
                answerStructure=0.40,
                confidenceOfAssessment=0.88,
                strengths=["High underlying technical concept comprehension"],
                missingConcepts=[],
                misconceptions=[],
                expressionIssues=["Unstructured answer opening", "Casual language phrasing"],
                evidence=["Demonstrated sound conceptual knowledge despite informal phrasing"],
                isStrugglingOrDontKnow=False,
                isExpressionUnclear=True,
                recommendedNextAction=AdaptiveAction.EXPRESSION_SCAFFOLD,
                recommendedReasonCode="high_knowledge_unclear_expression"
            )

        # 4. Deep technical answer
        strong_keywords = ["cosine", "bm25", "hybrid", "rerank", "cross-encoder", "hnsw", "pydantic", "react", "sharding", "latency", "precision", "recall", "paging", "cfs", "acid", "ioc", "jvm", "g1gc", "cgroups"]
        matches = [kw for kw in strong_keywords if kw in ans_clean]

        if len(matches) >= 2 or len(ans_clean) > 80:
            return AnswerEvaluation(
                technicalCorrectness=0.92,
                conceptualDepth=0.88,
                relevance=0.95,
                reasoning=0.90,
                application=0.88,
                expressionClarity=0.85,
                answerStructure=0.82,
                confidenceOfAssessment=0.94,
                strengths=[f"Accurately explained technical mechanisms ({', '.join(matches[:2]) if matches else 'core architecture'})", "Structured technical reasoning"],
                missingConcepts=[],
                misconceptions=[],
                expressionIssues=[],
                evidence=[f"Demonstrated solid understanding of {topic_name}"],
                isStrugglingOrDontKnow=False,
                isExpressionUnclear=False,
                recommendedNextAction=AdaptiveAction.GO_DEEPER,
                recommendedReasonCode="strong_fundamentals"
            )

        # 5. Standard answer
        return AnswerEvaluation(
            technicalCorrectness=0.75,
            conceptualDepth=0.60,
            relevance=0.80,
            reasoning=0.65,
            application=0.70,
            expressionClarity=0.70,
            answerStructure=0.65,
            confidenceOfAssessment=0.80,
            strengths=["Correct baseline definition"],
            missingConcepts=["Production trade-offs"],
            misconceptions=[],
            expressionIssues=[],
            evidence=[f"Understands basic application of {topic_name}"],
            isStrugglingOrDontKnow=False,
            isExpressionUnclear=False,
            recommendedNextAction=AdaptiveAction.GO_DEEPER,
            recommendedReasonCode="moderate_understanding"
        )

    def _mock_generate_question_text(
        self,
        action: AdaptiveAction,
        topic_name: str,
        day_number: int,
        target_depth: int,
        pending_evidence_item: Optional[str] = None,
        scaffold_prompt: Optional[str] = None,
        transfer_domain: Optional[str] = None,
        previous_answer: Optional[str] = None
    ) -> str:
        topic_lower = topic_name.lower()
        act_val = action.value if hasattr(action, 'value') else str(action)
        act_str = str(act_val).upper()

        # Subject-Specific Tailored Action Reframings
        if act_str == "RECOVER":
            if "operating systems" in topic_lower or "os" in topic_lower:
                return "Let's simplify process isolation: If a process tries to access memory outside its allocated bounds, how does an OS Segmentation Fault prevent memory corruption across processes?"
            if "dbms" in topic_lower or "database" in topic_lower or "sql" in topic_lower:
                return "Let's simplify database transactions: When executing two SQL queries where the second fails, how does a ROLLBACK restore the database to a valid state?"
            if "spring" in topic_lower or "boot" in topic_lower:
                return "Let's simplify Dependency Injection: Instead of creating a service using 'new UserService()', how does Spring's @Autowired annotation inject object instances at runtime?"
            if "java" in topic_lower:
                return "Let's simplify memory allocation: When an object is created using 'new MyClass()', is the object instance stored on the Heap memory or the Stack frame?"
            if "networks" in topic_lower:
                return "Let's simplify network connections: Before sending an HTTP GET request, what 3-way handshake packet sequence (SYN, SYN-ACK, ACK) establishes the TCP socket?"
            if "react" in topic_lower:
                return "Let's simplify component rendering: When useState updates a value in a React component, how does React determine which DOM elements need to update?"
            if "python" in topic_lower:
                return "Let's simplify concurrency: Because Python's GIL permits only one thread to execute CPython bytecode at a time, would you use multi-threading or multiprocessing for heavy CPU tasks?"
            if "docker" in topic_lower or "container" in topic_lower:
                return "Let's simplify containerization: How does a Docker container differ from a Virtual Machine in terms of sharing the host Linux kernel vs running a full guest OS?"
            return f"Let's simplify {topic_name}: At a fundamental level, what is the core input and expected output when using {topic_name} in a backend application?"

        if act_str == "EXPRESSION_SCAFFOLD":
            if "operating systems" in topic_lower or "os" in topic_lower:
                return "You clearly understand process memory. Try explaining it formally in three parts: 1) What virtual memory is, 2) How page tables translate virtual to physical addresses, and 3) Why this enforces isolation."
            if "dbms" in topic_lower or "database" in topic_lower or "sql" in topic_lower:
                return "You understand transaction safety. Structure your response into: 1) The definition of ACID properties, 2) How isolation levels prevent dirty reads, and 3) The trade-off between isolation and throughput."
            if "spring" in topic_lower or "boot" in topic_lower:
                return "You understand Spring's core benefit. Phrasing it for a senior technical interview: 1) Define Dependency Injection, 2) Explain how the ApplicationContext manages bean lifecycles, and 3) Give an example using @Component."
            if "java" in topic_lower:
                return "You understand Java memory layout. Present it cleanly: 1) Heap vs Stack allocation, 2) How the Garbage Collector identifies unreferenced objects, and 3) How volatile guarantees visibility."
            if "networks" in topic_lower:
                return "You understand network protocols. Structure your answer: 1) Purpose of the TCP 3-way handshake, 2) How sequence numbers are synchronized, and 3) How HTTP/2 multiplexing improves over HTTP/1.1."
            if "react" in topic_lower:
                return "You understand React state. Structure your explanation: 1) What the Virtual DOM is, 2) How the Fiber reconciler computes diffs, and 3) How useMemo avoids redundant calculations."
            return f"You have sound conceptual understanding of {topic_name}. Structure your response in three parts: 1) High-level definition, 2) Primary mechanism, and 3) Production trade-off."

        if act_str == "PROBE":
            if "operating systems" in topic_lower or "os" in topic_lower:
                return "You mentioned process memory isolation. Suppose two threads within the SAME process modify a shared global counter simultaneously without locks—what race condition occurs, and how do mutexes fix it?"
            if "dbms" in topic_lower or "database" in topic_lower or "sql" in topic_lower:
                return "You mentioned ACID isolation. Suppose two transactions execute under Read Committed isolation simultaneously—why can phantom reads still occur, and how does Serializable isolation prevent them?"
            if "spring" in topic_lower or "boot" in topic_lower:
                return "You mentioned Spring Bean creation. What happens if Bean A autowires Bean B, and Bean B autowires Bean A—how does Spring detect circular dependencies, and how do @Lazy or setter injection resolve it?"
            if "java" in topic_lower:
                return "You mentioned JVM Garbage Collection. If a long-running application holds static references to unused objects, will G1GC reclaim that memory—or will it trigger an OutOfMemoryError?"
            if "networks" in topic_lower:
                return "You mentioned TCP reliability. If a packet is lost in transit during a high-speed file transfer, how does TCP retransmission timeout (RTO) and fast retransmit repair the missing segment?"
            if "react" in topic_lower:
                return "You mentioned component state. What happens if you call setState directly inside the main render body without useEffect—how does React handle or prevent infinite re-render loops?"
            return f"You mentioned how {topic_name} works in normal operation. Suppose high traffic causes unexpected failure—what specific edge case or bottleneck occurs, and how do you mitigate it?"

        if act_str == "TRANSFER":
            domain = transfer_domain or "High-Throughput Enterprise Architecture"
            if "operating systems" in topic_lower or "os" in topic_lower:
                return f"You've shown strong depth in Operating Systems. Let's apply this: Imagine an ultra-low-latency Financial Trading Engine in {domain} processing 500,000 orders/sec. How would you configure CPU thread pinning (affinity), non-blocking lock-free queues, and kernel bypass?"
            if "dbms" in topic_lower or "database" in topic_lower or "sql" in topic_lower:
                return f"You've shown strong depth in DBMS. Let's apply this: Imagine a Global E-Commerce Platform in {domain} during Black Friday processing 100,000 checkout orders/min. How would you design database sharding, read replicas, and distributed Saga transactions?"
            if "spring" in topic_lower or "boot" in topic_lower:
                return f"You've shown strong depth in Spring Boot. Let's apply this: Imagine a Healthcare Patient Telemetry System in {domain} receiving streams from 50,000 devices. How would you architect Spring WebFlux reactive streams and distributed tracing?"
            if "java" in topic_lower:
                return f"You've shown strong depth in Core Java. Let's apply this: Imagine a Cybersecurity Log Analyzer in {domain} scanning 10GB/sec of logs. How would you leverage Java Memory-Mapped Files (ByteBuffer), Virtual Threads, and zero-copy parsing?"
            return f"You've shown strong depth in {topic_name}. Let's apply this to a real-world enterprise scenario in {domain}: How would you integrate {topic_name} to guarantee 99.99% uptime and fault tolerance?"

        # ---------------------------------------------------------------------
        # TOPIC & DEPTH-SPECIFIC TAILORED QUESTIONS (Zero repetition across depth)
        # ---------------------------------------------------------------------
        if "operating systems" in topic_lower or "os" in topic_lower:
            if target_depth >= 5:
                return "Production System Design in Operating Systems: How would you architect a custom non-blocking I/O event loop leveraging epoll/kqueue for 100k concurrent network connections?"
            elif target_depth == 4:
                return "Engineering deep-dive into Operating Systems: How does the Linux kernel handle page fault resolution, TLB cache misses, and thrashing under heavy memory allocations?"
            elif target_depth == 3:
                return "Applying Operating Systems: How do IPC mechanisms—like shared memory, pipes, and unix domain sockets—handle synchronization locks and race conditions?"
            elif target_depth == 2:
                return "Exploring Operating Systems: How do CPU scheduling algorithms (like Completely Fair Scheduler or Round Robin) handle context-switching overhead and CPU starvation?"
            else:
                return "Understanding Operating Systems: How would you explain virtual memory paging and thread vs. process isolation to a software engineer?"

        if "dbms" in topic_lower or "database" in topic_lower or "sql" in topic_lower:
            if target_depth >= 5:
                return "Production System Design in DBMS: How do write-ahead logging (WAL) and Multi-Version Concurrency Control (MVCC) guarantee zero data loss during hard node crashes?"
            elif target_depth == 4:
                return "Engineering deep-dive into DBMS & Databases: How do ACID transaction isolation levels (Repeatable Read vs Serializable) prevent write skew and phantom reads?"
            elif target_depth == 3:
                return "Applying DBMS: How do composite B+ Tree database indexes optimize multi-column query execution plans, and what are the write-amplification trade-offs?"
            elif target_depth == 2:
                return "Exploring DBMS: How do INNER, LEFT OUTER, and FULL OUTER JOINs differ in relational algebra execution, and how do database engines choose hash vs. merge joins?"
            else:
                return "Understanding DBMS: How would you explain ACID properties and primary key indexing trade-offs to a developer?"

        if "networks" in topic_lower or "computer networks" in topic_lower:
            if target_depth >= 5:
                return "Production System Design in Computer Networks: How do BGP routing protocols, TLS 1.3 zero-RTT handshakes, and CDN edge caching minimize global latency?"
            elif target_depth == 4:
                return "Engineering deep-dive into Computer Networks: How do TCP congestion control algorithms (like BBR/CUBIC) manage packet loss and head-of-line blocking in HTTP/2?"
            elif target_depth == 3:
                return "Applying Computer Networks: How do reverse proxies (like NGINX/HAProxy) execute SSL termination, load balancing, and rate limiting?"
            elif target_depth == 2:
                return "Exploring Computer Networks: How does a TCP 3-way handshake establish reliable socket connections, and how does recursive DNS resolution work?"
            else:
                return "Understanding Computer Networks: How would you explain the OSI model layers and the HTTP/1.1 vs HTTP/2 protocol evolution?"

        if "spring" in topic_lower or "spring boot" in topic_lower:
            if target_depth >= 5:
                return "Production System Design in Spring Boot: How do you configure Spring Cloud Circuit Breakers (Resilience4j) and distributed tracing (Micrometer/Zipkin) for microservice resilience?"
            elif target_depth == 4:
                return "Engineering deep-dive into Spring Boot: How does the Spring Container manage bean lifecycles and circular dependency resolution in a multi-module application?"
            elif target_depth == 3:
                return "Applying Spring Boot: How does Spring Data JPA manage transaction boundaries (@Transactional), entity lazy-loading, and N+1 query problems?"
            elif target_depth == 2:
                return "Exploring Spring Boot: How do Spring Security filters manage JWT authentication, CORS policies, and role-based authorization?"
            else:
                return "Understanding Spring Boot: How would you explain Dependency Injection (DI) and Inversion of Control (IoC) to a backend developer?"

        if "java" in topic_lower:
            if target_depth >= 5:
                return "Production System Design in Core Java: How do Virtual Threads (Project Loom) reduce platform thread allocation overhead in high-throughput reactive web applications?"
            elif target_depth == 4:
                return "Engineering deep-dive into Core Java: How does JVM Garbage Collection (G1GC / ZGC) track object reachability between Heap and Stack to minimize stop-the-world pauses?"
            elif target_depth == 3:
                return "Applying Core Java: How does the Java Memory Model manage thread safety, synchronized blocks, volatile variable visibility, and AtomicReference CAS operations?"
            elif target_depth == 2:
                return "Exploring Core Java: How do Java Collections (like HashMap vs ConcurrentHashMap) handle hash bucket collisions and red-black tree conversion?"
            else:
                return "Understanding Core Java: How would you explain OOP principles (Encapsulation, Polymorphism, Abstraction) and interface contract design in Java?"

        if "python" in topic_lower:
            if target_depth >= 5:
                return "Production System Design in Python: How do you design high-concurrency microservices using AsyncIO, UVLoop, and ProcessPoolExecutor to bypass GIL limits?"
            elif target_depth == 4:
                return "Engineering deep-dive into Python: How does the Global Interpreter Lock (GIL) impact multi-threaded CPU execution, and how do reference-counting and cyclic GC work?"
            elif target_depth == 3:
                return "Applying Python: How do decorators, generator iterators (`yield`), and context managers (`__enter__`/`__exit__`) work under the hood?"
            elif target_depth == 2:
                return "Exploring Python: How do Python lists, dictionaries, and memory allocations differ from C-style arrays and pointers?"
            else:
                return "Understanding Python: How would you explain dynamic typing, list comprehensions, and virtual environment isolation?"

        if "react" in topic_lower:
            if target_depth >= 5:
                return "Production System Design in React: How do Server-Side Rendering (SSR), Server Components, and Concurrent Mode optimize First Contentful Paint (FCP)?"
            elif target_depth == 4:
                return "Engineering deep-dive into React: How does the Fiber reconciliation engine schedule state updates and compute minimal Virtual DOM mutations?"
            elif target_depth == 3:
                return "Applying React: How do custom hooks, useCallback, useMemo, and Context API manage global state without causing excessive re-renders?"
            elif target_depth == 2:
                return "Exploring React: How does component state hydration work, and how do useEffect dependency arrays manage side effects?"
            else:
                return "Understanding React: How would you explain Virtual DOM diffing, JSX compilation, and props vs. state?"

        if "docker" in topic_lower or "kubernetes" in topic_lower or "container" in topic_lower:
            if target_depth >= 5:
                return "Production System Design in Kubernetes: How do Pod autoscaling (HPA), ingress controllers, and Service Mesh (Istio) manage zero-downtime rolling deployments?"
            elif target_depth == 4:
                return "Engineering deep-dive into Containerization: How do Linux cgroups and namespaces enforce memory/CPU limits and process isolation in Docker?"
            elif target_depth == 3:
                return "Applying Docker: How do multi-stage Docker builds separate build toolchains from runtime binaries to optimize image size and security?"
            elif target_depth == 2:
                return "Exploring Docker: How do Docker volumes, bridge networks, and image layer caching accelerate container builds?"
            else:
                return "Understanding Docker: How would you explain container images vs. virtual machines to a team?"

        if "aws" in topic_lower or "cloud" in topic_lower:
            if target_depth >= 5:
                return "Production System Design in AWS: How do you design multi-region active-active architectures using DynamoDB Global Tables, Route53, and S3 replication for 99.99% SLA?"
            elif target_depth == 4:
                return "Engineering deep-dive into AWS: How do IAM least-privilege policies, VPC security groups, and NAT Gateways secure private microservices?"
            elif target_depth == 3:
                return "Applying Cloud Architecture: How do SQS message queues and SNS topics execute asynchronous decoupled microservice event pipelines?"
            elif target_depth == 2:
                return "Exploring AWS: How do stateless EC2 auto-scaling groups and Application Load Balancers handle traffic spikes?"
            else:
                return "Understanding Cloud Infrastructure: How would you explain IaaS vs. PaaS vs. Serverless cloud models?"

        if "git" in topic_lower:
            if target_depth >= 5:
                return "Production System Design in Version Control: How do Git hooks, automated semantic release pipelines, and monorepo architectures manage enterprise codebases?"
            elif target_depth == 4:
                return "Engineering deep-dive into Git: How does Git structure its DAG object store (blobs, trees, commits, tags), and how does interactive rebase alter history?"
            elif target_depth == 3:
                return "Applying Git: How do git cherry-pick, stash, and bisect debug regression commits in complex branches?"
            elif target_depth == 2:
                return "Exploring Git: How do git rebase vs git merge strategies impact linear branch commit history?"
            else:
                return "Understanding Git: How would you explain Git branching models (GitFlow vs Trunk-Based) to a engineering team?"

        # Generic fallback per target depth (Zero repetition fallback)
        if target_depth >= 5:
            return f"Production System Architecture in {topic_name}: How would you optimize latency, throughput, and fault-tolerance under high load?"
        elif target_depth == 4:
            return f"Engineering deep-dive into {topic_name}: What are the primary failure modes in production, and how do you monitor and mitigate them?"
        elif target_depth == 3:
            return f"Applying {topic_name}: How would you construct a practical workflow combining data validation, logging, and error handling?"
        elif target_depth == 2:
            return f"Exploring {topic_name}: What are the key architectural trade-offs when choosing {topic_name} over alternative approaches?"
        else:
            return f"Understanding {topic_name}: How would you explain the core mechanism and primary use cases of {topic_name} to an engineering teammate?"

llm_service = LLMService()
