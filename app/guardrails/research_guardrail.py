from app.state.content_state import ContentState


def validate_research(state: ContentState) -> tuple[bool, list[str]]:
    """
    Validate the research produced by the Researcher Agent.

    Returns:
        (is_valid, errors)
    """

    errors = []

    research = state.get("research", [])
    sources = state.get("sources", [])

    # -------------------------
    # Research validation
    # -------------------------

    if not research:
        errors.append("Research output is missing.")

    elif not any(
        isinstance(item, str) and item.strip()
        for item in research
    ):
        errors.append("Research output is empty.")

    # Check whether the research contains
    # a reasonable amount of information.
    elif all(
        len(item.strip()) < 50
        for item in research
        if isinstance(item, str)
    ):
        errors.append("Research output is too short.")

    # -------------------------
    # Sources validation
    # -------------------------

    if not sources:
        errors.append("Research sources are missing.")

    # -------------------------
    # Final result
    # -------------------------

    is_valid = len(errors) == 0

    return is_valid, errors