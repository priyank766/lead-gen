from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=_api_key) if _api_key else None


def score_lead(lead: dict) -> tuple[int, dict]:
    """
    Scores a lead based on the completeness of its data.

    Args:
        lead: The lead dictionary to score.

    Returns:
        (score 0-100, breakdown dict)
    """
    breakdown = {
        "contact": 35 if lead.get("emails") else 0,
        "revenue": 25 if lead.get("phones") else 0,
        "industry": 15 if lead.get("linkedin") else 0,
        "intent": 15 if lead.get("has_pricing") else 0,
        "crosscheck": 10 if lead.get("has_contact_page") else 0,
    }
    score = sum(breakdown.values())
    return min(score, 100), breakdown


def get_score_justification(lead: dict, score: int, breakdown: dict) -> str:
    """
    Generates a concise, deterministic justification from the breakdown.

    Returns:
        A single-sentence string: "Justification: ..."
    """
    present = [k for k, v in breakdown.items() if v > 0]
    missing = [k for k, v in breakdown.items() if v == 0]
    parts = []
    if present:
        parts.append(f"has {', '.join(present)}")
    if missing:
        parts.append(f"missing {', '.join(missing)}")
    summary = "; ".join(parts) if parts else "insufficient data"
    return f"Justification: {summary}."


def main():
    """
    Main function to test the scorer.
    """
    test_lead = {
        "emails": ["test@example.com"],
        "phones": ["123-456-7890"],
        "linkedin": "linkedin.com/company/test",
        "has_contact_page": True,
        "has_pricing": False,
    }

    score = score_lead(test_lead)
    justification = get_score_justification(test_lead, score)
    print(f"Lead Score: {score}")
    print(f"Justification: {justification}")


if __name__ == "__main__":
    main()
