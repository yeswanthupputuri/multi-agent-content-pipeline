from app.state.content_state import ContentState


def validate_input(state: ContentState) -> tuple[bool, list[str]]:

    errors = []

    topic = state.get("topic", "")
    content_type = state.get("content_type", "")
    requirements = state.get("requirements", "")

    # -------------------------
    # Topic validation
    # -------------------------

    if not topic or not topic.strip():
        errors.append("Topic is required.")
    elif len(topic.strip()) < 5:
        errors.append("Topic is too short.")

    # -------------------------
    # Content type validation
    # -------------------------

    if not content_type or not content_type.strip():
        errors.append("Content type is required.")

    # -------------------------
    # Requirements validation
    # -------------------------

    if not requirements or not requirements.strip():
        errors.append("Content requirements are required.")
    elif len(requirements.strip()) < 10:
        errors.append("Content requirements are too short.")

    # -------------------------
    # Final result
    # -------------------------

    is_valid = len(errors) == 0

    return is_valid, errors