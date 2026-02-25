from validators.mandatory_rules import validate_mandatory

def test_mandatory_fields(company_df):
    for _, row in company_df.iterrows():
        for field in row.index:
            assert validate_mandatory(field, row[field])