from validators.entity_type_rules import validate_entity_type

def test_entity_type_rules(company_df):
    for _, row in company_df.iterrows():
        entity_type = row.get("category")
        assert validate_entity_type(entity_type, row)