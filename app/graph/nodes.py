from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.agents.editor import EditorAgent
from app.agents.fact_checker import FactCheckerAgent

from app.evaluation.metrics import (
    start_metrics,
    update_metrics,
    finish_metrics,
)

from app.guardrails.input_guardrail import validate_input
from app.guardrails.research_guardrail import validate_research
from app.guardrails.research_relevance_guardrail import (
    validate_research_relevance,
)
from app.guardrails.state_guardrail import (
    validate_state_for_writer,
    validate_state_for_editor,
    validate_state_for_fact_checker,
)
from app.guardrails.output_guardrail import validate_output

from app.llm.local_qwen import LocalQwen
from app.state.content_state import ContentState


def create_nodes(llm: LocalQwen):

    researcher = ResearcherAgent(llm)
    writer = WriterAgent(llm)
    editor = EditorAgent(llm)
    fact_checker = FactCheckerAgent(llm)

    # ---------------------------------------------------------
    # Input Guardrail
    # ---------------------------------------------------------

    def input_guardrail_node(
        state: ContentState
    ) -> ContentState:

        valid, errors = validate_input(state)

        if not valid:
            state["errors"] = errors
            state["status"] = "input_validation_failed"

        metrics = state.get("metrics", {})

        if "started_at" not in metrics:

            thread_id = metrics.get(
                "thread_id",
                "unknown"
            )

            start_metrics(
                state,
                thread_id
            )

        return state

    # ---------------------------------------------------------
    # Researcher
    # ---------------------------------------------------------

    def researcher_node(
        state: ContentState
    ) -> ContentState:

        return researcher.research(state)

    # ---------------------------------------------------------
    # Research Guardrail
    # ---------------------------------------------------------

    def research_guardrail_node(
        state: ContentState
    ) -> ContentState:

        valid, errors = validate_research(state)

        if not valid:

            state["errors"] = errors
            state["status"] = "research_validation_failed"

        return state

    # ---------------------------------------------------------
    # Research Relevance Guardrail
    # ---------------------------------------------------------

    def research_relevance_guardrail_node(
        state: ContentState
    ) -> ContentState:

        valid, errors = validate_research_relevance(
            state,
            llm
        )

        # Research is relevant
        if valid:

            state["status"] = "research_validated"

            return state

        # Research is not relevant
        state["research_relevance_feedback"] = (
            errors[0]
            if errors
            else "Research is not relevant."
        )

        # Maximum research attempts reached
        if state.get(
            "research_attempt_count",
            0
        ) >= 2:

            state["errors"] = errors

            state["status"] = (
                "research_relevance_validation_failed"
            )

        # Research attempt failed, retry researcher
        else:

            state["status"] = (
                "research_relevance_failed"
            )

        return state

    # ---------------------------------------------------------
    # Writer State Guardrail
    # ---------------------------------------------------------

    def writer_state_guardrail_node(
        state: ContentState
    ) -> ContentState:

        valid, errors = validate_state_for_writer(state)

        if not valid:

            state["errors"] = errors
            state["status"] = (
                "writer_state_validation_failed"
            )

        return state

    # ---------------------------------------------------------
    # Writer
    # ---------------------------------------------------------

    def writer_node(
        state: ContentState
    ) -> ContentState:

        # Existing draft means this is a revision
        if state.get("draft"):

            state["revision_count"] = (
                state.get(
                    "revision_count",
                    0
                ) + 1
            )

        return writer.write(state)

    # ---------------------------------------------------------
    # Editor State Guardrail
    # ---------------------------------------------------------

    def editor_state_guardrail_node(
        state: ContentState
    ) -> ContentState:

        valid, errors = validate_state_for_editor(state)

        if not valid:

            state["errors"] = errors
            state["status"] = (
                "editor_state_validation_failed"
            )

        return state

    # ---------------------------------------------------------
    # Editor
    # ---------------------------------------------------------

    def editor_node(
        state: ContentState
    ) -> ContentState:

        state = editor.edit(state)

        update_metrics(
            state,
            editor_decision=True
        )

        # Stop if maximum revisions reached
        if (
            state.get("editor_decision") != "approve"
            and state.get(
                "revision_count",
                0
            ) >= 3
        ):

            state["status"] = (
                "max_revisions_reached"
            )

        return state

    # ---------------------------------------------------------
    # Fact Checker State Guardrail
    # ---------------------------------------------------------

    def fact_checker_state_guardrail_node(
        state: ContentState
    ) -> ContentState:

        valid, errors = validate_state_for_fact_checker(
            state
        )

        if not valid:

            state["errors"] = errors
            state["status"] = (
                "fact_checker_state_validation_failed"
            )

        return state

    # ---------------------------------------------------------
    # Fact Checker
    # ---------------------------------------------------------

    def fact_checker_node(
        state: ContentState
    ) -> ContentState:

        state = fact_checker.check(state)

        claims_checked = len(
            state.get(
                "fact_check_results",
                []
            )
        )

        update_metrics(
            state,
            fact_check_decision=True,
            claims_checked=claims_checked
        )

        # Stop if maximum revisions reached
        if (
            state.get("fact_check_decision")
            != "verified"
            and state.get(
                "revision_count",
                0
            ) >= 3
        ):

            state["status"] = (
                "max_revisions_reached"
            )

        return state

    # ---------------------------------------------------------
    # Output Guardrail
    # ---------------------------------------------------------

    def output_guardrail_node(
        state: ContentState
    ) -> ContentState:

        valid, errors = validate_output(state)

        if not valid:

            state["errors"] = errors
            state["status"] = (
                "output_validation_failed"
            )

        else:

            state["status"] = "completed"

        finish_metrics(state)

        return state

    # ---------------------------------------------------------
    # Metrics Finalizer
    # ---------------------------------------------------------

    def metrics_finalizer_node(
        state: ContentState
    ) -> ContentState:

        finish_metrics(state)

        return state

    # ---------------------------------------------------------
    # Return all graph nodes
    # ---------------------------------------------------------

    return {

        "input_guardrail":
            input_guardrail_node,

        "researcher":
            researcher_node,

        "research_guardrail":
            research_guardrail_node,

        "research_relevance_guardrail":
            research_relevance_guardrail_node,

        "writer_state_guardrail":
            writer_state_guardrail_node,

        "writer":
            writer_node,


        "editor_state_guardrail":
            editor_state_guardrail_node,

        "editor":
            editor_node,

        "fact_checker_state_guardrail":
            fact_checker_state_guardrail_node,

        "fact_checker":
            fact_checker_node,

        "output_guardrail":
            output_guardrail_node,

        "metrics_finalizer":
            metrics_finalizer_node,
    }