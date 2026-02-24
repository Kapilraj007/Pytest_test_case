from data_quality_engine.validators.source_tier_validator import assign_source_tier

def test_sec_is_tier1():
    result = assign_source_tier("SEC 10-K", "Regulatory Filing")
    assert result["source_tier"] == 1
