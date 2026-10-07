from app.llm.local_qwen import LocalQwen
from app.state.content_state import ContentState


class ResearcherAgent:

    def __init__(self, llm: LocalQwen):
        self.llm = llm

    def research(self, state: ContentState) -> ContentState:

        topic = state.get("topic", "")
        content_type = state.get("content_type", "")
        requirements = state.get("requirements", "")

        attempt_count = state.get(
            "research_attempt_count",
            0
        ) + 1

        state["research_attempt_count"] = attempt_count

        previous_feedback = state.get(
            "research_relevance_feedback",
            ""
        )

        feedback_section = ""

        if previous_feedback:
            feedback_section = f"""
Previous research was rejected because:

{previous_feedback}

You MUST correct this problem in the new research.
"""

        prompt = f"""
You are a careful research assistant preparing factual research
for another AI agent that will write content.

TARGET TOPIC:
{topic}

CONTENT TYPE:
{content_type}

REQUIREMENTS:
{requirements}

{feedback_section}

IMPORTANT RESEARCH RULES:

1. Research ONLY the intended target topic.
2. Determine the intended meaning of the topic from the topic
   AND the requirements together.
3. If the topic has multiple possible meanings, use the meaning
   that best matches the requirements.
4. Do not confuse similarly named people, companies, technologies,
   products, frameworks, protocols, or organizations.
5. Do not invent facts.
6. Do not create fictional products, projects, organizations,
   statistics, dates, people, or achievements.
7. If you are uncertain about a fact, do not present it as fact.
8. Do not use unrelated information simply because it shares
   the same name as the target topic.
9. Research should directly help satisfy the requirements.
10. Do not write the final article.

Provide:

1. A clear definition of the target topic.
2. Key facts and concepts directly related to the target topic.
3. Important points required by the user's requirements.
4. Potential factual claims that should later be verified.
5. Relevant sources, organizations, or documentation that could
   be consulted.

Before producing the research, internally verify that the research
is about the TARGET TOPIC and not another entity with a similar name.

Provide only research notes.
"""

        response = self.llm.generate(prompt)

        state["research"] = [response]

        state["sources"] = [
            "Sources mentioned or suggested by the local research model"
        ]

        return state