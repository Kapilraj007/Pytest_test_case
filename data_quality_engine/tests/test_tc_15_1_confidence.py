
from data_quality_engine.validators.confidence_validator import validate_confidence

def test_llm_inferred_low_confidence():
    result = validate_confidence({
        "generation_method": "LLM_Inferred"
    })
    assert result["Confidence_Level"] == "Low"
