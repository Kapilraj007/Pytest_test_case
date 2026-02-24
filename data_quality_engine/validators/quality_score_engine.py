
from data_quality_engine.config.quality_weights import FIELD_WEIGHTS

def compute_quality_score(record):
    score = 0
    for field, weight in FIELD_WEIGHTS.items():
        if record.get(field) not in [None, ""]:
            score += weight

    recency = record.get("recency_status")
    if recency == "Outdated":
        score = min(score, 0.75)

    if not record.get("revenue") and not record.get("funding"):
        score = min(score, 0.65)

    return score

def assign_grade(score):
    if score >= 0.90:
        return "A"
    elif score >= 0.75:
        return "B"
    elif score >= 0.60:
        return "C"
    else:
        return "D"
