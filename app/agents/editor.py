from app.llm.local_qwen import LocalQwen
from app.state.content_state import ContentState


class EditorAgent:

    def __init__(self, llm: LocalQwen):
        self.llm = llm

    def edit(self, state: ContentState) -> ContentState:

        topic = state.get("topic", "")
        content_type = state.get("content_type", "")
        requirements = state.get("requirements", "")
        draft = state.get("draft", "")

        prompt = f"""
You are a strict professional editor.

Review the following draft.

Topic:
{topic}

Content type:
{content_type}

Requirements:
{requirements}

Draft:
{draft}

Evaluate the draft for:

1. Relevance to the topic
2. Whether the requirements are followed
3. Structure and clarity
4. Missing important information
5. Unsupported or questionable claims
6. Repetition or unnecessary content
7. Overall quality

You must return EXACTLY this format:

DECISION: APPROVE

FEEDBACK: <your concise feedback>

OR:

DECISION: REJECT

FEEDBACK: <what needs to be improved>

Do not rewrite the article.
Only provide the decision and feedback.
"""

        response = self.llm.generate(prompt)

        # Default decision if the model does not
        # produce the expected format.
        decision = "reject"
        feedback = response

        lines = response.splitlines()

        for line in lines:

            if line.upper().startswith("DECISION:"):
                decision_value = line.split(":", 1)[1].strip().lower()

                if decision_value in {"approve", "reject"}:
                    decision = decision_value

            elif line.upper().startswith("FEEDBACK:"):
                feedback = line.split(":", 1)[1].strip()

        state["editor_decision"] = decision
        state["editor_feedback"] = feedback

        return state