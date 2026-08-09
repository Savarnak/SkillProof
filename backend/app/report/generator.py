from typing import List, Dict, Any, Tuple
from app.interview.schemas import InterviewState, QuestionTurn, MisconceptionStatus
from app.schemas.candidate import Candidate
from app.report.schemas import (
    DiscoveryReportData, RefinementDiff, CoachedAnswer, MisconceptionInsight,
    PersistentGapInsight, KnowledgeVsExpressionInsight, ActionPlan, GrowthItem,
    ProgressChangeItem, WeightedScoreBreakdown
)
from app.report.aggregator import report_aggregator

class AnswerRefiner:
    """Generates crisp, highly topic-specific interview-ready answer refinements preserving candidate demonstrated knowledge."""

    TOPIC_REFINEMENTS = {
        "operating_systems": "Virtual memory uses page tables to map virtual addresses to physical RAM frames, isolating process memory and preventing memory corruption across processes.",
        "dbms": "ACID transaction isolation levels control database concurrency: Read Committed prevents dirty reads, while Serializable eliminates phantom reads using locks or multi-version concurrency control (MVCC).",
        "spring_boot": "Dependency Injection decouples class implementation from object creation by delegating bean lifecycle management to the Spring IoC container via annotations like @Autowired and @Component.",
        "core_java": "The JVM Garbage Collector tracks object reachability on the Heap to reclaim unreferenced memory during GC cycles, while volatile and synchronized keywords guarantee memory visibility across CPU caches.",
        "computer_networks": "The TCP 3-way handshake (SYN, SYN-ACK, ACK) synchronizes sequence numbers before data transmission, while HTTP/2 multiplexes streams over a single connection to eliminate head-of-line blocking.",
        "react": "React Virtual DOM diffing compares component trees asynchronously using the Fiber reconciliation engine, batching state updates to minimize costly direct DOM manipulations.",
        "docker": "Multi-stage Docker builds separate build toolchains from runtime binaries, creating minimal, secure container images with reduced attack surface.",
        "aws": "Stateless microservices auto-scale horizontally behind an Elastic Load Balancer, using IAM roles for least-privilege resource access and S3 for durable object storage.",
        "git": "Git rebase rewrites commit history by re-applying local commits onto the target branch tip, preserving a clean linear history compared to merge commits.",
        "python": "The Python Global Interpreter Lock (GIL) enforces single-threaded CPython execution per process, making multiprocessing or asyncio necessary for CPU-bound tasks.",
        "sql": "SQL query execution plans use indexes (B-Trees) to avoid full table scans, using inner/outer JOINs and window functions to aggregate relational data efficiently."
    }

    @classmethod
    def refine_answer(cls, topic_id: str, topic_name: str, original_answer: str) -> str:
        ans = original_answer.strip()
        if not ans:
            return f"For {topic_name}, I would structure the response: 1) High-level definition, 2) Primary mechanism, and 3) Production trade-offs."

        ans_clean = ans.rstrip('.')
        t_clean = topic_id.lower().replace("top_", "")

        for key, refined in cls.TOPIC_REFINEMENTS.items():
            if key in t_clean or key in topic_name.lower():
                return f"{ans_clean}. Specifically, {refined}"

        if "vector" in t_clean or "similarity" in topic_name.lower():
            return f"{ans_clean}. Vector spaces map embeddings where metrics like cosine similarity measure vector direction independently of magnitude."
        if "hnsw" in t_clean or "indexing" in topic_name.lower():
            return f"{ans_clean}. HNSW constructs a multi-layer graph to achieve logarithmic search complexity for approximate nearest neighbors."
        if "chunking" in t_clean or "hybrid" in topic_name.lower():
            return f"{ans_clean}. Document chunking balances context boundaries while hybrid search merges BM25 lexical precision with dense vector embeddings."

        return f"{ans_clean} — Structured into: 1) Core mechanism, 2) Primary use case, and 3) Production trade-offs."

class ReportGenerator:
    """Generates complete evidence-backed candidate discovery reports with Post-Interview Intelligence."""

    @staticmethod
    def select_delivery_formula(turn_question: str, topic_name: str, depth_level: int) -> Tuple[str, List[str]]:
        q_lower = turn_question.lower()
        if depth_level >= 5 or "architecture" in q_lower or "design" in q_lower or "system" in q_lower:
            return (
                "SYSTEM DESIGN",
                ["1. Clarify problem", "2. Propose architecture", "3. Explain decisions", "4. Discuss trade-offs", "5. Scalability/reliability"]
            )
        if "vs" in q_lower or "compare" in q_lower or "differ" in q_lower or "metric" in q_lower:
            return (
                "TECHNICAL COMPARISON",
                ["1. Define both", "2. Key difference", "3. When to use each", "4. Trade-off"]
            )
        if "experience" in q_lower or "project" in q_lower or "mission" in q_lower:
            return (
                "EXPERIENCE QUESTION",
                ["1. Situation", "2. Task", "3. Action", "4. Result"]
            )
        return (
            "CONCEPT QUESTION",
            ["1. Define it", "2. Explain how it works", "3. Give an example", "4. Mention when useful"]
        )

    @staticmethod
    def identify_root_cause(turn: QuestionTurn) -> str:
        if not turn.evaluation:
            return "Lack of explicit system trade-off details"
        ev = turn.evaluation
        if ev.isStrugglingOrDontKnow:
            return "Expressed uncertainty / lack of knowledge"
        if ev.misconceptions:
            return "Misconception regarding core mechanism"
        if ev.isExpressionUnclear or ev.expressionClarity < 0.60:
            return "Unclear structure or informal phrasing"
        if ev.application < 0.60:
            return "Weak example or lack of practical context"
        if ev.conceptualDepth < 0.60:
            return "Missing core concept or trade-off detail"
        return "Lack of explicit system design trade-offs"

    @classmethod
    def generate_discovery_report(
        cls,
        state: InterviewState,
        candidate: Candidate,
        curriculum_title: str
    ) -> DiscoveryReportData:
        # 1. Weighted scores calculation
        weighted = report_aggregator.calculate_weighted_scores(state)

        # 2. Topic evidence expanders
        expanders = report_aggregator.build_topic_evidence_expanders(state)

        # 3. Knowledge vs Expression Insight
        k_score = weighted.technicalKnowledge
        e_score = weighted.expression
        show_insight = False
        insight_msg = None

        if k_score >= 0.50 and (e_score < 0.65 or k_score - e_score >= 0.08):
            show_insight = True
            headline_txt = "You knew it. You just didn't show it clearly."
            tech_demo = "Your underlying technical comprehension across core concepts was solid."
            comm_impact = "Informal answer structure or casual opening phrasing made it harder to recognize your depth immediately."
            how_imp = "Lead with a crisp 1-sentence technical definition, then explain the mechanism using our Delivery Formula."
            insight_msg = f"Your underlying technical understanding ({int(k_score*100)}%) was strong. The main opportunity is structuring your explanation so the interviewer can recognize your knowledge faster."
        elif e_score >= 0.70 and k_score < 0.65:
            show_insight = True
            headline_txt = "Clear communication, but technical details need deepening."
            tech_demo = "Your delivery style was articulate, well-structured, and easy to follow."
            comm_impact = "However, specific low-level mechanisms, failure modes, and architectural trade-offs were incomplete."
            how_imp = "Focus study on internal algorithm mechanics, edge cases, and quantitative performance trade-offs."
            insight_msg = f"Your communication ({int(e_score*100)}%) was clear and structured. The main opportunity is deepening your technical mechanism details and trade-offs."
        else:
            headline_txt = "Balanced technical knowledge and communication delivery."
            tech_demo = "Demonstrated baseline alignment between conceptual knowledge and verbal delivery."
            comm_impact = "Clear communication without major structural blockers."
            how_imp = "Continue refining real-world production system design scenarios."

        kv_insight = KnowledgeVsExpressionInsight(
            show=show_insight,
            headline=headline_txt,
            technicalDemonstrated=tech_demo,
            communicationImpact=comm_impact,
            howToImprove=how_imp
        )

        # 4. Coached Answers & Refinement Diffs
        coached_answers: List[CoachedAnswer] = []
        refinement_diffs: List[RefinementDiff] = []

        for turn in state.conversationHistory:
            if turn.candidate_answer and turn.evaluation and turn.evaluation.technicalCorrectness > 0.10:
                t_assessment = state.topicsAssessed.get(turn.topic_id)
                t_name = t_assessment.topic_name if t_assessment else turn.topic_id

                formula_name, formula_steps = cls.select_delivery_formula(turn.question_text, t_name, turn.depth_level)
                root_cause = cls.identify_root_cause(turn)
                polished = AnswerRefiner.refine_answer(turn.topic_id, t_name, turn.candidate_answer)

                strengths_list = turn.evaluation.strengths or ["Demonstrated core conceptual attempt"]

                coached_answers.append(
                    CoachedAnswer(
                        questionIndex=turn.turn_index,
                        questionText=turn.question_text,
                        originalAnswer=turn.candidate_answer,
                        strengths=strengths_list,
                        whatHeldItBack=root_cause,
                        interviewReadyVersion=polished,
                        deliveryFormulaName=formula_name,
                        deliveryFormulaSteps=formula_steps
                    )
                )

                refinement_diffs.append(
                    RefinementDiff(
                        questionIndex=turn.turn_index,
                        questionText=turn.question_text,
                        originalAnswer=turn.candidate_answer,
                        interviewReadyVersion=polished,
                        diffAdditions=["Direct technical opening", "Explicit trade-off", "Clear component sequence"],
                        diffDeletions=["Informal phrasing", "Unnecessary repetition"],
                        deliveryFormula=" -> ".join(formula_steps),
                        whatWasGood=", ".join(strengths_list),
                        whatCouldImprove=root_cause
                    )
                )

        # 5. Misconception Insights
        misc_insights: List[MisconceptionInsight] = []
        for item in state.misconceptions:
            m_txt = item.misconception
            m_low = m_txt.lower()

            if "hallucinat" in m_low:
                true_txt = "RAG reduces hallucinations by grounding responses in retrieved document passages, but incorrect chunking or embedding noise can still cause hallucinations."
                mental_model = "Mental Model: RAG acts like an open-book exam—if the textbook passage retrieved is wrong or missing, the answer can still be wrong."
            elif "pgvector" in m_low or "ram" in m_low:
                true_txt = "Vector search indexes (HNSW/IVF) rely heavily on RAM caching for fast distance computations."
                mental_model = "Mental Model: High-dimensional vector graphs reside in RAM for sub-10ms traversal."
            else:
                true_txt = f"Core mechanism of {item.topic} operates deterministically based on input parameters and systemic constraints."
                mental_model = f"Mental Model: Trace input -> processing pipeline -> system trade-off."

            st_val = "Resolved" if item.status == MisconceptionStatus.RESOLVED else ("Partially resolved" if item.status == MisconceptionStatus.PROBED else "Unresolved")

            misc_insights.append(
                MisconceptionInsight(
                    topic=item.topic,
                    misconception=m_txt,
                    whatsActuallyTrue=true_txt,
                    howToRememberIt=mental_model,
                    status=st_val
                )
            )

        # 6. Longitudinal Memory Growth & Persistent Gap Insights
        from app.memory.service import candidate_memory_service
        growth_items: List[GrowthItem] = []
        progress_items: List[ProgressChangeItem] = []
        gap_insights: List[PersistentGapInsight] = []
        is_first_time = True

        try:
            mem_ctx = candidate_memory_service.get_relevant_context(candidate.candidate_id)
            if mem_ctx.recent_memories or mem_ctx.total_previous_interviews > 0 or mem_ctx.growth_history or mem_ctx.recurring_gaps:
                is_first_time = False

            for g_event in mem_ctx.growth_history:
                growth_items.append(GrowthItem(
                    topic=g_event.topic,
                    previousLevel=g_event.previous_level,
                    currentLevel=g_event.current_level,
                    growthAmount=g_event.growth,
                    evidence=g_event.evidence
                ))
                progress_items.append(ProgressChangeItem(
                    topic=g_event.topic,
                    previousStatus=f"Level {g_event.previous_level} (Developing)",
                    currentStatus=f"Level {g_event.current_level} (Strong)",
                    changeTag="Improved"
                ))

            for p_gap in mem_ctx.recurring_gaps:
                gap_insights.append(PersistentGapInsight(
                    topic=p_gap.topic,
                    whyItMatters=f"{p_gap.topic} is a foundational requirement for senior technical roles.",
                    whatToPractice=f"Review internal mechanics, edge cases, and production failure modes for {p_gap.topic}.",
                    suggestedNextChallenge=f"Complete a dedicated deep-dive challenge on {p_gap.topic}.",
                    isResolved=False
                ))
        except Exception:
            pass

        # 7. Action Plan (Exactly 3 Actionable Next Steps based on Evidence)
        next_steps = []
        if e_score < 0.65:
            next_steps.append("Practice explaining your core technical concept in under 60 seconds using the Definition -> Mechanism -> Trade-off formula.")
        else:
            next_steps.append("Practice delivering high-level architecture decisions using the System Design Delivery Formula.")

        if state.knowledgeGaps:
            top_gap = state.knowledgeGaps[0]
            next_steps.append(f"Build a hands-on proof-of-concept pipeline focusing on {top_gap}.")
        else:
            next_steps.append("Build a small hybrid retrieval pipeline combining BM25 keyword search with vector embeddings.")

        next_steps.append("Revisit failure modes, boundary edge cases, and quantitative performance trade-offs under high load.")

        action_plan = ActionPlan(nextSteps=next_steps[:3])

        playbook = [
            {"scenario": "When asked 'What is X?'", "formula": "Definition -> Purpose -> Real-world Example"},
            {"scenario": "When asked 'How does X work?'", "formula": "Input -> Process / Algorithm -> Output"},
            {"scenario": "When asked 'Why X instead of Y?'", "formula": "Choice -> Performance Reason -> Operational Trade-off"},
            {"scenario": "For System Architecture", "formula": "Requirements -> Architecture -> Trade-offs -> Failure Modes"}
        ]

        transfer_status = f"Successfully transferred core concepts to {len(state.transferChallengesUsed)} real-world scenario(s)" if len(state.transferChallengesUsed) > 0 else "Concept transfer not attempted"

        return DiscoveryReportData(
            interviewId=state.interviewId,
            candidateName=candidate.name,
            curriculumTitle=curriculum_title,
            totalQuestionsAsked=state.questionCount,
            uniqueDaysCovered=len(state.curriculumDaysCovered),
            weightedScores=weighted,
            topicEvidenceExpanders=expanders,
            demonstratedStrengths=state.strengths[:5] or ["Solid foundational technical knowledge"],
            knowledgeGaps=state.knowledgeGaps[:5],
            expressionGaps=state.expressionGaps[:5],
            showKnowledgeVsExpressionInsight=show_insight,
            insightMessage=insight_msg,
            knowledgeVsExpressionInsight=kv_insight,
            misconceptionsFound=state.misconceptions,
            misconceptionInsights=misc_insights,
            profileDivergenceNotes=state.profileVsEvidenceDivergence,
            transferAbility=transfer_status,
            interviewMode=state.interviewMode,
            jdRequirementCoverage=state.jdRequirementCoverage,
            refinementDiffs=refinement_diffs[:4],
            coachedAnswers=coached_answers[:4],
            personalPlaybookFormulas=playbook,
            isFirstTimeCandidate=is_first_time,
            growthSummary=growth_items,
            whatChangedSinceLastInterview=progress_items,
            persistentGapInsights=gap_insights,
            actionPlan=action_plan,
            summaryFeedback=f"Candidate evaluated across {state.questionCount} questions covering {len(state.curriculumDaysCovered)} curriculum topics. Overall readiness: {weighted.overallReadiness}/100."
        )

report_generator = ReportGenerator()
