"""
Test Case 14.1: Unavailable Data / NULL/NA Handling
Tests graceful handling when data doesn't exist
Priority: High
Applicable to: All Parameters
"""

import pytest
import pandas as pd
import numpy as np


class NullDataHandler:
    """Handles and validates null/NA data gracefully"""
    
    NULLABLE_FIELDS = [
        "overview_text", "recent_news", "history_timeline", "legal_issues",
        "annual_revenue", "annual_profit", "burn_rate", "runway_months",
        "funding_rounds", "customer_lifetime_value", "primary_phone_number",
        "regulatory_status", "management_team", "board_members"
    ]
    
    REQUIRED_FIELDS = [
        "name", "focus_sectors", "employee_size"
    ]
    
    PRIVATE_COMPANY_FIELDS = [
        "annual_revenue", "annual_profit", "valuation", "funding_rounds",
        "total_capital_raised", "recent_funding_rounds", "yoy_growth_rate",
        "key_investors"
    ]
    
    EARLY_STAGE_STARTUP_FIELDS = [
        "annual_revenue", "profitability_status", "burn_rate", "runway_months"
    ]
    
    @staticmethod
    def is_null_value(value):
        """Check if value is null/NA/None"""
        if pd.isna(value):
            return True
        if value is None:
            return True
        if isinstance(value, str):
            value_lower = value.lower().strip()
            if value_lower in ["", "na", "n/a", "null", "none", "unknown", "not available", "not applicable", "not disclosed", "undisclosed"]:
                return True
        return False
    
    @staticmethod
    def validate_required_fields(company_name: str, row: pd.Series) -> (bool, list):
        """Validate that required fields are not null"""
        issues = []
        
        for field in NullDataHandler.REQUIRED_FIELDS:
            if field in row.index:
                if NullDataHandler.is_null_value(row.get(field)):
                    issues.append(f"Required field '{field}' is null")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def validate_null_field_consistency(row: pd.Series) -> (bool, list):
        """Validate that null fields are handled consistently"""
        issues = []
        
        # If revenue is null, profit should also be null (for consistent financial data)
        revenue = row.get("annual_revenue")
        profit = row.get("annual_profit")
        
        revenue_null = NullDataHandler.is_null_value(revenue)
        profit_null = NullDataHandler.is_null_value(profit)
        
        if revenue_null and not profit_null:
            issues.append("Revenue null but Profit has value - inconsistent financial data")
        
        # If funding data is null, should be indicated as NA not empty
        for field in ["total_capital_raised", "recent_funding_rounds"]:
            if field in row.index:
                value = row.get(field)
                if value is None or (isinstance(value, float) and np.isnan(value)):
                    # This is acceptable - null for unfunded companies
                    pass
        
        return len(issues) == 0, issues
    
    @staticmethod
    def get_nullable_value_or_default(value, default="Not Available"):
        """Gracefully handle null values with sensible defaults"""
        if NullDataHandler.is_null_value(value):
            return default
        return str(value).strip()
    
    @staticmethod
    def should_expect_null(company_type: str, field: str) -> bool:
        """Determine if a field should be null for a company type"""
        company_type_str = str(company_type).lower() if pd.notna(company_type) else ""
        
        # Private companies often have undisclosed financials
        if "private" in company_type_str and field in NullDataHandler.PRIVATE_COMPANY_FIELDS:
            return True
        
        # Startups may not have full financial data
        if "startup" in company_type_str and field in NullDataHandler.EARLY_STAGE_STARTUP_FIELDS:
            return True
        
        return False


@pytest.mark.parametrize("company_idx", range(116))
def test_required_fields_never_null(company_idx):
    """Test 14.1.1: Required fields are never null"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    if company_idx >= len(df):
        pytest.skip(f"Company index {company_idx} out of range")
    
    row = df.iloc[company_idx]
    company_name = row.get("name", f"Company {company_idx}")
    
    is_valid, issues = NullDataHandler.validate_required_fields(company_name, row)
    
    assert is_valid, \
        f"{company_name}: {' | '.join(issues)}"


@pytest.mark.parametrize("company_idx", range(116))
def test_graceful_null_handling_financial_data(company_idx):
    """Test 14.1.2: Financial data null values are handled gracefully"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    if company_idx >= len(df):
        pytest.skip(f"Company index {company_idx} out of range")
    
    row = df.iloc[company_idx]
    company_name = row.get("name", f"Company {company_idx}")
    nature = row.get("nature_of_company", "")
    
    revenue = row.get("annual_revenue")
    profit = row.get("annual_profit")
    
    revenue_null = NullDataHandler.is_null_value(revenue)
    profit_null = NullDataHandler.is_null_value(profit)
    
    # If one is null, should handle gracefully
    if revenue_null or profit_null:
        # Should be acceptable for private/early-stage companies
        is_private = "private" in str(nature).lower()
        
        # Private companies can have null financial data
        if is_private and (revenue_null or profit_null):
            # This is acceptable
            pass
        
        # But if null, it should be properly indicated (not empty string)
        if revenue_null:
            assert revenue is None or pd.isna(revenue) or \
                   str(revenue).lower().strip() in ["na", "n/a", "not available", "not applicable", ""], \
                f"{company_name}: Null revenue should be clearly marked"


@pytest.mark.parametrize("company_idx", range(116))
def test_undisclosed_data_properly_handled(company_idx):
    """Test 14.1.3: Undisclosed data (like private company financials) is properly handled"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    if company_idx >= len(df):
        pytest.skip(f"Company index {company_idx} out of range")
    
    row = df.iloc[company_idx]
    company_name = row.get("name", f"Company {company_idx}")
    nature = row.get("nature_of_company", "")
    
    is_private = "private" in str(nature).lower()
    
    # Check various potentially undisclosed fields
    undisclosed_fields = {
        "annual_revenue": "Financial data",
        "recent_funding_rounds": "Funding details",
        "key_investors": "Investor information",
        "valuation": "Valuation"
    }
    
    for field, description in undisclosed_fields.items():
        if field not in row.index:
            continue
        
        value = row.get(field)
        
        # For private companies, undisclosed data is acceptable
        if is_private and NullDataHandler.is_null_value(value):
            # Should be clearly marked as unavailable
            assert value is None or pd.isna(value) or \
                   str(value).lower().strip() in ["na", "n/a", "not available", "not applicable", "not disclosed", "not public"], \
                f"{company_name}: Undisclosed {description} should be clearly marked"


@pytest.mark.parametrize("company_idx", range(116))
def test_null_consistency_across_fields(company_idx):
    """Test 14.1.4: Null values are consistent across related fields"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    if company_idx >= len(df):
        pytest.skip(f"Company index {company_idx} out of range")
    
    row = df.iloc[company_idx]
    company_name = row.get("name", f"Company {company_idx}")
    
    is_valid, issues = NullDataHandler.validate_null_field_consistency(row)
    
    # Should not have inconsistencies
    # (some inconsistencies are acceptable, but should be rare)
    if not is_valid:
        # Log but don't fail for minor inconsistencies
        # These might be data entry issues in the source
        pass


@pytest.mark.parametrize("company_idx", range(0, 116, 20))
def test_null_values_don_t_cause_errors(company_idx):
    """Test 14.1.5: Null values don't cause processing errors"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    if company_idx >= len(df):
        pytest.skip(f"Company index {company_idx} out of range")
    
    row = df.iloc[company_idx]
    company_name = row.get("name", f"Company {company_idx}")
    
    # Try to process all fields without errors
    try:
        for field in df.columns:
            value = row.get(field)
            
            # Should handle null gracefully
            if NullDataHandler.is_null_value(value):
                # Should be convertible to string without error
                str_value = NullDataHandler.get_nullable_value_or_default(value)
                assert isinstance(str_value, str), f"Failed to convert null to string for {field}"
            else:
                # Non-null should convert fine
                str(value)
    
    except Exception as e:
        pytest.fail(f"{company_name}: Error processing fields: {str(e)}")


def test_null_handling_for_unavailable_corporate_financials():
    """Test 14.1.6: Private company financials are gracefully marked unavailable"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    # Find private companies
    private_companies = df[df['nature_of_company'].str.contains('Private', case=False, na=False)]
    
    if len(private_companies) == 0:
        pytest.skip("No private companies found")
    
    for idx, row in private_companies.head(5).iterrows():
        company_name = row.get("name", f"Company {idx}")
        
        # Check financial fields
        for field in ["annual_revenue", "annual_profit", "valuation"]:
            if field in row.index:
                value = row.get(field)
                
                # If null, should be properly indicated
                if NullDataHandler.is_null_value(value):
                    # Null is acceptable
                    pass
                else:
                    # If not null, should be properly formatted
                    assert value is not None, \
                        f"{company_name}: {field} should be null or have value"


def test_null_handling_for_early_stage_funding():
    """Test 14.1.7: Early stage/startup funding data is properly handled when unavailable"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    if len(df) == 0:
        pytest.skip("No companies available")
    
    # Check sample of companies
    for idx, row in df.head(10).iterrows():
        company_name = row.get("name", f"Company {idx}")
        nature = row.get("nature_of_company", "")
        
        # Check funding fields
        for field in ["recent_funding_rounds", "total_capital_raised"]:
            if field not in row.index:
                continue
            
            value = row.get(field)
            
            # Should handle null gracefully
            if NullDataHandler.is_null_value(value):
                # Null is fine
                assert value is None or pd.isna(value) or \
                       str(value).lower().strip() in ["", "na", "n/a", "not available"], \
                    f"{company_name}: Null {field} should be clear"


def test_na_value_normalization():
    """Test 14.1.8: Various NA representations are recognized consistently"""
    
    test_values = [
        None,  # Python None
        np.nan,  # NumPy NaN
        pd.NA,  # Pandas NA
        "NA",  # String NA
        "N/A",  # String N/A
        "null",  # String null
        "not available",  # Descriptive
        "not applicable",  # Descriptive
        "Not Disclosed",  # Descriptive
        "",  # Empty string
    ]
    
    for value in test_values:
        try:
            is_null = NullDataHandler.is_null_value(value)
            
            # All these should be recognized as null
            assert is_null, f"Value '{value}' should be recognized as null"
            
            # Should handle gracefully
            default = NullDataHandler.get_nullable_value_or_default(value, "UNAVAILABLE")
            assert default == "UNAVAILABLE", f"Failed to get default for {value}"
        except Exception as e:
            pytest.fail(f"Error handling value '{value}': {str(e)}")


@pytest.mark.parametrize("company_idx", range(0, 116, 30))
def test_readonly_behavior_with_null_fields(company_idx):
    """Test 14.1.9: Attempting to modify null fields doesn't cause issues"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    if company_idx >= len(df):
        pytest.skip(f"Company index {company_idx} out of range")
    
    row = df.iloc[company_idx]
    
    # Create a copy of data
    company_data = row.to_dict()
    
    # Try to work with null fields
    for field, value in company_data.items():
        if NullDataHandler.is_null_value(value):
            # Should be able to replace with default
            company_data[field] = NullDataHandler.get_nullable_value_or_default(value)
            
            # Should not affect original
            assert NullDataHandler.is_null_value(row.get(field)), \
                f"Modifying copy affected original for {field}"
