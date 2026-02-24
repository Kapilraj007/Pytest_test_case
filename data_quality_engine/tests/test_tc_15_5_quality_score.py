
from data_quality_engine.validators.quality_score_engine import compute_quality_score, assign_grade
def test_grade_a():
    record = {
        "revenue": "2B",
        "funding": "1B",
        "logo": "logo.png",
        "website": "site.com",
        "recency_status": "Recent",
        "accuracy": 0.95
    }
    score = compute_quality_score(record)
    grade = assign_grade(score)
    assert grade in ["A", "B", "C", "D"]
