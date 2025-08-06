# app/memory/scoring.py


def score_importance(text: str) -> float:
    """
    Heuristic scoring of importance.
    Returns a float between 0.0 (not important) and 1.0 (very important).
    """
    keywords = [
        "urgent",
        "asap",
        "important",
        "call",
        "meeting",
        "deadline",
        "fail",
        "alert",
    ]
    score = sum(1 for word in keywords if word in text.lower())
    return min(score / len(keywords), 1.0)
