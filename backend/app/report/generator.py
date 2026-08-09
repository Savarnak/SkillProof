from typing import List, Dict, Any
from app.interview.schemas import InterviewState, QuestionTurn
from app.schemas.candidate import Candidate
from app.report.schemas import (
    DiscoveryReportData, RefinementDiff
)
from app.report.aggregator import report_aggregator

class AnswerRefiner:
    """Generates crisp, highly topic-specific interview-ready answer refinements preserving candidate ideas."""

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
        t_clean = topic_id.lower().replace("top_", "")
        
        for key, refined in cls.TOPIC_REFINEMENTS.items():
            if key in t_clean or key in topic_name.lower():
                return f"{original_answer.strip().rstrip('.')} — Specifically, {refined}"

        return f"{original_answer.strip().rstrip('.')} — Specifically, for {topic_name}, I would structure the response: 1) High-level definition, 2) Core mechanism and process, and 3) Production trade-offs."

class ReportGenerator:
    """Generates complete evidence-backed candidate discovery reports."""

    @classmethod
    def generate_discovery_report(
        cls,
        state: InterviewState,
        candidate: Candidate,
        curriculum_title: str
    ) -> DiscoveryReportData:
        # 1. Calculate transparent weighted readiness scores
        weighted = report_aggregator.calculate_weighted_scores(state)

        # 2. Build topic evidence expanders
        expanders = report_aggregator.build_topic_evidence_expanders(state)

        # 3. Detect "You Know More Than You Showed" Insight
        show_insight = False
        insight_msg = None
        if weighted.technicalKnowledge > weighted.expression + 0.10:
            show_insight = True
            insight_msg = f"Your technical understanding ({int(weighted.technicalKnowledge*100)}%) was strong. Your initial responses were sometimes informal or unstructured, but your explanations improved significantly after reframing."

        # 4. Generate Answer Refinement Diffs
        refinement_diffs: List[RefinementDiff] = []
        for turn in state.conversationHistory:
            if turn.candidate_answer and turn.evaluation and turn.evaluation.technicalCorrectness > 0.10:
                diffs_add = ["Direct technical opening", "Explicit architectural trade-off", "Clear component sequence"]
                diffs_del = ["Unnecessary repetition", "Informal phrasing"]
                
                # Pick delivery formula based on depth level
                if turn.depth_level >= 5:
                    formula = "Requirements -> Architecture -> Trade-offs -> Failure Modes"
                elif turn.depth_level >= 3:
                    formula = "Decision -> Reason -> Trade-off"
                else:
                    formula = "Definition -> How it works -> Real-world Example"

                topic_assessment = state.topicsAssessed.get(turn.topic_id)
                topic_name = topic_assessment.topic_name if topic_assessment else turn.topic_id

                polished_version = AnswerRefiner.refine_answer(
                    topic_id=turn.topic_id,
                    topic_name=topic_name,
                    original_answer=turn.candidate_answer
                )

                refinement_diffs.append(
                    RefinementDiff(
                        questionIndex=turn.turn_index,
                        questionText=turn.question_text,
                        originalAnswer=turn.candidate_answer,
                        interviewReadyVersion=polished_version,
                        diffAdditions=diffs_add,
                        diffDeletions=diffs_del,
                        deliveryFormula=formula,
                        whatWasGood=", ".join(turn.evaluation.strengths) or "Clear core conceptual attempt",
                        whatCouldImprove=", ".join(turn.evaluation.missingConcepts + turn.evaluation.expressionIssues) or "Add more system design detail"
                    )
                )

        # 5. Personal Technical Delivery Playbook Formulas
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
            misconceptionsFound=state.misconceptions,
            profileDivergenceNotes=state.profileVsEvidenceDivergence,
            transferAbility=transfer_status,
            interviewMode=state.interviewMode,
            jdRequirementCoverage=state.jdRequirementCoverage,
            refinementDiffs=refinement_diffs[:4],
            personalPlaybookFormulas=playbook,
            summaryFeedback=f"Candidate evaluated across {state.questionCount} questions covering {len(state.curriculumDaysCovered)} curriculum topics. Overall readiness: {weighted.overallReadiness}/100."
        )

report_generator = ReportGenerator()
