"""
Test Case 12.5: Risk Classification
Tests appropriate risk level assignment for different risk categories (burn rate, customer concentration, geopolitical)
Priority: Medium
"""

import pytest
import pandas as pd
import json


def classify_burn_rate_risk(burn_rate_value):
    """Classify burn rate into risk levels"""
    if pd.isna(burn_rate_value) or burn_rate_value == "NA":
        return "Low"  # Not applicable means cash-flow positive
    
    value_str = str(burn_rate_value).lower()
    
    if "not applicable" in value_str or "cash-flow positive" in value_str or "profitable" in value_str:
        return "Low"
    elif "zero" in value_str or "0" in value_str:
        return "Low"
    elif "$" in value_str:
        # Extract amount if possible
        try:
            parts = value_str.split("$")
            if len(parts) > 1:
                amount_str = parts[1].split()[0].replace("m", "").replace("k", "")
                amount = float(amount_str)
                if amount < 1:  # Less than $1M/month
                    return "Low"
                elif amount < 5:  # Less than $5M/month
                    return "Medium"
                else:
                    return "High"
        except:
            return "Medium"
    return "Medium"


def classify_customer_concentration_risk(concentration_value):
    """Classify customer concentration into risk levels"""
    if pd.isna(concentration_value) or concentration_value == "NA":
        return "Low"
    
    value_str = str(concentration_value).lower()
    
    if "yes" in value_str and ("top" in value_str or "%" in value_str):
        # Extract percentage if available
        try:
            import re
            percentages = re.findall(r'(\d+)%', value_str)
            if percentages:
                pct = int(percentages[0])
                if pct > 50:
                    return "Critical"
                elif pct > 30:
                    return "High"
                elif pct > 15:
                    return "Medium"
        except:
            pass
        return "Medium"
    elif "no" in value_str or "diversified" in value_str:
        return "Low"
    elif "low" in value_str:
        return "Low"
    
    return "Medium"


def classify_geopolitical_risk(geo_value):
    """Classify geopolitical risk into levels"""
    if pd.isna(geo_value) or geo_value == "NA":
        return "Low"
    
    value_str = str(geo_value).lower()
    risk_count = len([x for x in value_str.split(";") if x.strip()])
    
    if risk_count >= 3:
        return "High"
    elif risk_count >= 2:
        return "Medium"
    else:
        return "Low"


@pytest.mark.parametrize("company_idx", range(116))
def test_burn_rate_risk_classification(company_idx):
    """Test 12.5.1: Appropriate burn rate risk assignment"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    if company_idx >= len(df):
        pytest.skip(f"Company index {company_idx} out of range")
    
    row = df.iloc[company_idx]
    burn_rate = row.get("burn_rate", "NA")
    company_name = row.get("name", f"Company {company_idx}")
    
    risk_level = classify_burn_rate_risk(burn_rate)
    
    # Risk level should be one of the valid classifications
    assert risk_level in ["Low", "Medium", "High"], \
        f"{company_name}: Burn rate risk classification failed"
    
    # If it's a profitability statement, should be Low risk
    if pd.notna(burn_rate):
        burn_str = str(burn_rate).lower()
        if "not applicable" in burn_str or "profitable" in burn_str or "cash-flow positive" in burn_str:
            assert risk_level == "Low", \
                f"{company_name}: Profitable companies should have Low burn rate risk"


@pytest.mark.parametrize("company_idx", range(116))
def test_customer_concentration_risk_classification(company_idx):
    """Test 12.5.2: Appropriate customer concentration risk assignment"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    if company_idx >= len(df):
        pytest.skip(f"Company index {company_idx} out of range")
    
    row = df.iloc[company_idx]
    concentration = row.get("customer_concentration_risk", "NA")
    company_name = row.get("name", f"Company {company_idx}")
    
    risk_level = classify_customer_concentration_risk(concentration)
    
    # Risk level should be one of the valid classifications
    assert risk_level in ["Low", "Medium", "High", "Critical"], \
        f"{company_name}: Customer concentration risk classification failed"
    
    # High concentration should not be classified as Low
    if pd.notna(concentration):
        conc_str = str(concentration).lower()
        if "yes" in conc_str and ">" in conc_str and "50%" in conc_str:
            assert risk_level in ["High", "Critical"], \
                f"{company_name}: High concentration should have High/Critical risk"


@pytest.mark.parametrize("company_idx", range(116))
def test_geopolitical_risk_classification(company_idx):
    """Test 12.5.3: Appropriate geopolitical risk level assignment"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    if company_idx >= len(df):
        pytest.skip(f"Company index {company_idx} out of range")
    
    row = df.iloc[company_idx]
    geo_risks = row.get("geopolitical_risks", "NA")
    company_name = row.get("name", f"Company {company_idx}")
    
    risk_level = classify_geopolitical_risk(geo_risks)
    
    # Risk level should be one of the valid classifications
    assert risk_level in ["Low", "Medium", "High"], \
        f"{company_name}: Geopolitical risk classification failed"
    
    # Multiple risks should be classified appropriately
    if pd.notna(geo_risks):
        risk_count = len([x for x in str(geo_risks).split(";") if x.strip()])
        if risk_count >= 3:
            assert risk_level == "High", \
                f"{company_name}: Multiple geopolitical risks should result in High classification"


def test_risk_classification_consistency():
    """Test 12.5.4: Risk classification is consistent across similar companies"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    # Get public profitable companies
    public_companies = df[df['nature_of_company'].str.contains('Public', case=False, na=False)]
    
    if len(public_companies) > 0:
        for idx, row in public_companies.head(5).iterrows():
            burn_rate = row.get("burn_rate", "NA")
            risk = classify_burn_rate_risk(burn_rate)
            
            # Profitable public companies should have Low risk
            if pd.notna(burn_rate) and "cash-flow positive" in str(burn_rate).lower():
                assert risk == "Low", \
                    f"Public profitable company should have Low burn rate risk"
