from validators.default_value_rules import validate_default

def test_default_values(company_df):
    for _, row in company_df.iterrows():
        for field in row.index:
            assert validate_default(field, row[field])