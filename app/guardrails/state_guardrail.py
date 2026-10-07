from app.state.content_state import ContentState


def validate_state_for_writer(
    state: ContentState
) -> tuple[bool, list[str]]:

    errors = []

    if not state.get("research"):
        errors.append("Research is missing.")

    if not state.get("sources"):
        errors.append("Sources are missing.")

    return len(errors) == 0, errors


def validate_state_for_editor(
    state: ContentState
) -> tuple[bool, list[str]]:

    errors = []

    if not state.get("draft"):
        errors.append("Draft is missing.")

    return len(errors) == 0, errors


def validate_state_for_fact_checker(
    state: ContentState
) -> tuple[bool, list[str]]:

    errors = []

    if not state.get("draft"):
        errors.append("Draft is missing.")

    if not state.get("research"):
        errors.append("Research is missing.")

    return len(errors) == 0, errors