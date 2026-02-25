from validators.null_propagation_rules import validate_null_propagation

def test_null_propagation(company_df):
    for _, row in company_df.iterrows():
        for field in row.index:
            assert validate_null_propagation(field, row)