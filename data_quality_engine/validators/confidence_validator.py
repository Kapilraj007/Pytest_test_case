
def validate_confidence(record):
    generation_method = record.get("generation_method")
    source = record.get("source")
    derivation_logic = record.get("derivation_logic")
    confidence = record.get("Confidence_Level")

    if generation_method == "LLM_Inferred":
        return {"Confidence_Level": "Low", "Is_Estimated": True}

    if source and "SEC" in source:
        return {"Confidence_Level": "High", "Is_Estimated": False}

    if derivation_logic:
        return {"Flag": "Estimated"}

    if confidence == "High" and not source:
        raise ValueError("High confidence requires verified source")

    return {"Confidence_Level": confidence or "Medium"}
