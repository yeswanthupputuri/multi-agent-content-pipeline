from app.state.content_state import ContentState


MAX_REVISIONS = 3


def route_after_input(state: ContentState) -> str:

    if state.get("status") == "input_validation_failed":
        return "end"

    return "researcher"


def route_after_research(state: ContentState) -> str:

    if state.get("status") == "research_validation_failed":
        return "end"

    return "research_relevance_guardrail"


def route_after_research_relevance(
    state: ContentState
) -> str:

    status = state.get("status")

    # Research relevance check failed permanently
    if status == "research_relevance_validation_failed":
        return "end"

    # Research is irrelevant but another research attempt
    # is still allowed
    if status == "research_relevance_failed":
        return "researcher"

    # Research is relevant
    return "writer_state_guardrail"


def route_after_writer_state(state: ContentState) -> str:

    if state.get("status") == "writer_state_validation_failed":
        return "end"

    return "writer"


def route_after_editor_state(state: ContentState) -> str:

    if state.get("status") == "editor_state_validation_failed":
        return "end"

    return "editor"


def route_after_editor(state: ContentState) -> str:

    decision = state.get(
        "editor_decision",
        "reject"
    )

    revision_count = state.get(
        "revision_count",
        0
    )

    # Editor approved the draft
    if decision == "approve":
        return "fact_checker_state_guardrail"

    # Editor rejected the draft and revision limit
    # has been reached
    if revision_count >= MAX_REVISIONS:
        state["status"] = "max_revisions_reached"
        return "end"

    # Editor rejected the draft and another revision
    # is allowed
    return "writer"


def route_after_fact_checker_state(
    state: ContentState
) -> str:

    if (
        state.get("status")
        == "fact_checker_state_validation_failed"
    ):
        return "end"

    return "fact_checker"


def route_after_fact_checker(
    state: ContentState
) -> str:

    decision = state.get(
        "fact_check_decision",
        ""
    )

    revision_count = state.get(
        "revision_count",
        0
    )

    # All claims passed fact checking
    if decision == "verified":
        return "output_guardrail"

    # Fact checking failed and revision limit
    # has been reached
    if revision_count >= MAX_REVISIONS:
        state["status"] = "max_revisions_reached"
        return "end"

    # Fact checking found problems and another
    # revision is allowed
    return "writer"


def route_after_output(state: ContentState) -> str:

    return "end"