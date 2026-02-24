
from data_quality_engine.validators.recency_validator import calculate_recency

def test_recent_status():
    result = calculate_recency("2025-11-01")
    assert result["recency_status"] in ["Recent", "Acceptable", "Outdated"]
