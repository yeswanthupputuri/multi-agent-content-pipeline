from app.llm.local_qwen import LocalQwen
from app.state.content_state import ContentState


class WriterAgent:

    def __init__(self, llm: LocalQwen):
        self.llm = llm

    def write(self, state: ContentState) -> ContentState:

        topic = state.get("topic", "")
        content_type = state.get("content_type", "")
        requirements = state.get("requirements", "")

        research = state.get("research", [])
        sources = state.get("sources", [])

        draft = state.get("draft", "")
        editor_feedback = state.get("editor_feedback", "")

        fact_check_results = state.get(
            "fact_check_results",
            []
        )

        revision_count = state.get(
            "revision_count",
            0
        )

        research_text = "\n\n".join(research)
        sources_text = "\n".join(sources)

        # ---------------------------------------------------------
        # First draft
        # ---------------------------------------------------------

        if revision_count == 0:

            prompt = f"""
You are a professional content writer.

Create the requested content using the research provided below.

Topic:
{topic}

Content type:
{content_type}

Requirements:
{requirements}

Research:
{research_text}

Sources:
{sources_text}

Instructions:

1. Use the research as the factual foundation.
2. Follow the requested content type.
3. Follow all requirements.
4. Organize the content clearly.
5. Do not invent unsupported facts.
6. Do not mention that you are an AI.
7. Produce only the draft content.

Write the complete draft now.
"""

        # ---------------------------------------------------------
        # Revision
        # ---------------------------------------------------------

        else:

            # Convert fact-check results into readable text.
            fact_check_text = ""

            for result in fact_check_results:

                fact_check_text += f"""
Claim:
{result.get("claim", "")}

Status:
{result.get("status", "")}

Reason:
{result.get("reason", "")}

---
"""

            prompt = f"""
You are a professional content writer revising an existing draft.

Topic:
{topic}

Content type:
{content_type}

Requirements:
{requirements}

Research:
{research_text}

Sources:
{sources_text}

Previous Draft:
{draft}

Editor Feedback:
{editor_feedback}

Fact-Check Findings:
{fact_check_text}

Revision Number:
{revision_count}

Instructions:

Instructions:

1. Revise the previous draft based on the editor and fact-checking feedback.
2. Fix every questionable or unsupported factual claim.
3. Remove factual claims that cannot be supported by the research.
4. Preserve factual claims that are already supported by the research.
5. Do NOT introduce any new factual claims.
6. Every factual statement in the revised draft must be supported by the
   provided research.
7. Do NOT use outside knowledge.
8. Do NOT add new technical details that are not present in the research.
9. Do NOT expand the article by inventing examples, capabilities,
   statistics, comparisons, predictions, or technical explanations.
10. If a questionable claim cannot be repaired using the research,
    remove it instead.
11. You may improve grammar, wording, organization and readability.
12. Continue following the original content requirements.
13. Do not mention the editing or fact-checking process.
14. Produce only the complete revised draft.

Write the complete revised draft now.
"""

        response = self.llm.generate(prompt)

        state["draft"] = response
        state["status"] = "draft_created"

        return state