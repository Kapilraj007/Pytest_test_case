
from data_quality_engine.config.source_tier_mapping import SOURCE_TIERS

def assign_source_tier(source_name, source_type):
    tier = SOURCE_TIERS.get(source_type) or SOURCE_TIERS.get(source_name)
    if not tier:
        return {"source_tier": 3, "validation_message": "Caution: Unverified Source"}
    return {"source_tier": tier, "is_verified": tier in [1,2]}

def resolve_multiple_sources(sources):
    tiers = []
    for src in sources:
        tier = SOURCE_TIERS.get(src, 3)
        tiers.append(tier)
    return {"source_tier": min(tiers)}
