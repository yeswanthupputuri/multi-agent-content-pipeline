from app.state.content_state import ContentState


def validate_output(
    state: ContentState
) -> tuple[bool, list[str]]:

    errors = []

    draft = state.get("draft", "")
    fact_check_decision = state.get(
        "fact_check_decision",
        ""
    )

    if not draft or not draft.strip():
        errors.append("Final draft is missing.")

    if fact_check_decision != "verified":
        errors.append(
            "Final content has not passed fact checking."
        )

    is_valid = len(errors) == 0

    return is_valid, errors