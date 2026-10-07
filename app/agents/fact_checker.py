import re

from app.llm.local_qwen import LocalQwen
from app.state.content_state import ContentState


class FactCheckerAgent:

    def __init__(self, llm: LocalQwen):
        self.llm = llm

    def extract_claims(self, draft: str) -> list[str]:
        """
        Extract factual sentences from the draft.

        Markdown headings are ignored because they are section
        labels rather than factual claims.
        """

        # Remove Markdown heading lines completely.
        cleaned_text = re.sub(
            r"^\s*#+\s*.*$",
            "",
            draft,
            flags=re.MULTILINE
        )

        # Split text into sentences.
        sentences = re.split(
            r"(?<=[.!?])\s+",
            cleaned_text
        )

        claims = []

        for sentence in sentences:

            sentence = sentence.strip()

            # Ignore empty or very short fragments.
            if len(sentence) < 20:
                continue

            claims.append(sentence)

        return claims

    def check_claim(
        self,
        claim: str,
        research_text: str
    ) -> dict:

        prompt = f"""
You are a strict evidence-based fact-checking assistant.

Your ONLY job is to determine whether the RESEARCH explicitly supports
the CLAIM.

RESEARCH:
{research_text}

CLAIM:
{claim}

Use ONLY the information contained in RESEARCH.

Important rules:

1. Do NOT use outside knowledge.
2. Do NOT assume information that is not explicitly present.
3. Do NOT treat a claim as supported just because it sounds reasonable.
4. If only part of the claim is supported, mark it QUESTIONABLE.
5. If the research provides no evidence for the claim, mark it UNSUPPORTED.
6. Claims containing words such as:
   "best", "most", "significantly", "rapidly",
   "completely", "always", "never", "more accurately"
   require explicit evidence.
7. Predictions about the future require explicit evidence.
8. Claims about superiority or effectiveness require explicit evidence.
9. The explanation must identify the specific research statement
   that supports or fails to support the claim.

Return EXACTLY:

STATUS: SUPPORTED
REASON: <specific evidence from the research>

OR:

STATUS: QUESTIONABLE
REASON: <explain which part lacks sufficient evidence>

OR:

STATUS: UNSUPPORTED
REASON: <explain that the research provides no evidence or contradicts it>

Do not rewrite the claim.
Do not add outside facts.
Provide only STATUS and REASON.
"""

        response = self.llm.generate(prompt)

        status = "questionable"
        reason = response.strip()

        for line in response.splitlines():

            line = line.strip()

            if line.upper().startswith("STATUS:"):

                value = line.split(":", 1)[1].strip().lower()

                if value in {
                    "supported",
                    "questionable",
                    "unsupported"
                }:
                    status = value

            elif line.upper().startswith("REASON:"):

                reason = line.split(":", 1)[1].strip()

        return {
            "claim": claim,
            "status": status,
            "reason": reason
        }

    def check(self, state: ContentState) -> ContentState:

        research = state.get("research", [])
        draft = state.get("draft", "")

        research_text = "\n\n".join(research)

        claims = self.extract_claims(draft)

        fact_check_results = []

        for claim in claims:

            result = self.check_claim(
                claim,
                research_text
            )

            fact_check_results.append(result)

        state["fact_check_results"] = fact_check_results

        problematic_claims = [
            result
            for result in fact_check_results
            if result["status"] in {
                "questionable",
                "unsupported"
            }
        ]

        if problematic_claims:
            state["fact_check_decision"] = "needs_revision"
        else:
            state["fact_check_decision"] = "verified"

        state["status"] = "fact_checked"

        return state