from app.llm.local_qwen import LocalQwen
from app.state.content_state import ContentState


MAX_RESEARCH_ATTEMPTS = 2


def validate_research_relevance(
    state: ContentState,
    llm: LocalQwen
) -> tuple[bool, list[str]]:

    topic = state.get("topic", "")
    requirements = state.get("requirements", "")
    research = state.get("research", [])

    if not research:
        return False, ["Research is missing."]

    research_text = "\n\n".join(research)

    prompt = f"""
You are a strict research relevance checker.

Determine whether the RESEARCH is about the exact TARGET TOPIC
and satisfies the user's REQUIREMENTS.

TARGET TOPIC:
{topic}

REQUIREMENTS:
{requirements}

RESEARCH:
{research_text}

Rules:

1. The research must discuss the intended target topic.
2. Use the requirements to determine the intended meaning when
   the topic is ambiguous.
3. Do not consider research relevant merely because it shares
   a word with the target topic.
4. The research must contain information useful for satisfying
   the requirements.
5. Reject research about a different person, company, product,
   technology, organization, or concept.
6. Reject research containing obviously invented or unrelated
   information.
7. Do not use outside knowledge.

Return EXACTLY:

DECISION: RELEVANT
FEEDBACK: <brief explanation>

OR:

DECISION: IRRELEVANT
FEEDBACK: <brief explanation of what is wrong>

Do not rewrite the research.
"""

    response = llm.generate(prompt)

    decision = "irrelevant"
    feedback = response.strip()

    for line in response.splitlines():

        line = line.strip()

        if line.upper().startswith("DECISION:"):

            value = (
                line
                .split(":", 1)[1]
                .strip()
                .lower()
            )

            if value in {"relevant", "irrelevant"}:
                decision = value

        elif line.upper().startswith("FEEDBACK:"):

            feedback = (
                line
                .split(":", 1)[1]
                .strip()
            )

    state["research_relevance_decision"] = decision
    state["research_relevance_feedback"] = feedback

    if decision == "relevant":
        return True, []

    return False, [feedback]