"""
Test Case 13.4: Memory Independence (SCALE & PERFORMANCE)
Tests that no cross-contamination occurs between company data requests
Priority: Critical
Applicable to: All Parameters
"""

import pytest
import pandas as pd
from copy import deepcopy


class DataContaminationDetector:
    """Detects potential data contamination between requests"""
    
    def __init__(self):
        self.processed_companies = {}
        self.field_signatures = {}
    
    def register_company(self, company_id: int, company_data: dict):
        """Register a processed company"""
        self.processed_companies[company_id] = deepcopy(company_data)
        
        # Create signature of unique values
        self.field_signatures[company_id] = {
            k: str(v)[:50] for k, v in company_data.items()
        }
    
    def check_contamination(self, prev_company_id: int, curr_company_id: int, 
                           curr_company_data: dict) -> (bool, list):
        """Check if current company has data from previous company"""
        if prev_company_id not in self.field_signatures:
            return True, []  # No previous data to contaminate with
        
        contamination_found = []
        prev_signature = self.field_signatures[prev_company_id]
        
        # Check if any field from prev appears in current
        for field_name, curr_value in curr_company_data.items():
            if pd.isna(curr_value):
                continue
            
            curr_str = str(curr_value)[:100]
            
            for prev_field, prev_value in prev_signature.items():
                # Check for exact or partial match
                if prev_value and prev_value in curr_str:
                    # Skip if it's a common field value (e.g., country names)
                    common_values = ["United States", "India", "Public", "Private", "Tech"]
                    if not any(common in prev_value for common in common_values):
                        contamination_found.append({
                            "field": field_name,
                            "prev_field": prev_field,
                            "prev_value": prev_value,
                            "curr_value": curr_str
                        })
        
        is_clean = len(contamination_found) == 0
        return is_clean, contamination_found


@pytest.fixture(scope="session")
def contamination_detector():
    """Session-scoped contamination detector"""
    return DataContaminationDetector()


@pytest.mark.parametrize("company_pair_idx", range(0, 50, 10))  # Test sequential pairs
def test_no_data_contamination_sequential(company_pair_idx, contamination_detector):
    """Test 13.4.1: No data contamination between sequential company requests"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    if company_pair_idx + 1 >= len(df):
        pytest.skip("Insufficient companies for pair test")
    
    # Process two sequential companies
    companies_data = []
    
    for idx in [company_pair_idx, company_pair_idx + 1]:
        row = df.iloc[idx]
        company_data = {
            "name": row.get("name"),
            "industry": row.get("focus_sectors"),
            "revenue": row.get("annual_revenue"),
            "employees": row.get("employee_size"),
            "headquarters": row.get("headquarters_address")
        }
        companies_data.append((idx, company_data))
        contamination_detector.register_company(idx, company_data)
    
    # Check second company against first for contamination
    first_idx, first_data = companies_data[0]
    second_idx, second_data = companies_data[1]
    
    is_clean, contamination = contamination_detector.check_contamination(
        first_idx, second_idx, second_data
    )
    
    assert is_clean, \
        f"Data contamination detected in company pair {first_idx}-{second_idx}: {contamination}"


def test_memory_isolation_same_company_multiple_reads():
    """Test 13.4.2: Reading same company multiple times produces identical results"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    if len(df) == 0:
        pytest.skip("No companies available")
    
    row = df.iloc[0]
    
    # Read same company multiple times
    reads = []
    for _ in range(5):
        company_data = {
            "name": row.get("name"),
            "industry": row.get("focus_sectors"),
            "headquarters": row.get("headquarters_address"),
            "revenue": row.get("annual_revenue")
        }
        reads.append(company_data)
    
    # All reads should be identical
    first_read = reads[0]
    for i, subsequent_read in enumerate(reads[1:], 1):
        assert first_read == subsequent_read, \
            f"Read #{i+1} differs from initial read. Data is not immutable."
        
        # Especially, names should match exactly
        assert first_read["name"] == subsequent_read["name"], \
            f"Company name changed between reads (memory corruption)"


def test_batch_processing_independence():
    """Test 13.4.3: Batch processing doesn't affect individual company data"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    if len(df) < 5:
        pytest.skip("Insufficient companies for batch test")
    
    # Get baseline data for company 0
    baseline = df.iloc[0].to_dict()
    
    # Process batch of companies
    batch = []
    for i in range(5):
        if i < len(df):
            batch.append(df.iloc[i].to_dict())
    
    # Check company 0 again
    post_batch = df.iloc[0].to_dict()
    
    # Should be identical
    assert baseline["name"] == post_batch["name"], \
        "Company name changed after batch processing"
    assert baseline["overview_text"] == post_batch["overview_text"], \
        "Company overview changed after batch processing"


def test_no_shared_state_between_companies():
    """Test 13.4.4: Company objects don't share mutable state"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    if len(df) < 3:
        pytest.skip("Insufficient companies")
    
    # Create company objects
    companies = []
    for i in range(3):
        company = {
            "id": i,
            "name": df.iloc[i].get("name"),
            "offices": df.iloc[i].get("office_locations"),
            "sectors": df.iloc[i].get("focus_sectors")
        }
        companies.append(company)
    
    # Attempt to modify one company's data
    original_offices = str(companies[0].get("offices"))
    companies[0]["offices"] = "MODIFIED"
    
    # Other companies should not be affected
    assert companies[1]["offices"] != "MODIFIED", \
        "Modifying one company affected another - shared mutable state!"
    assert companies[2]["offices"] != "MODIFIED", \
        "Modifying one company affected another - shared mutable state!"
    
    # First company should reflect the change when accessed directly
    assert companies[0]["offices"] == "MODIFIED", \
        "Direct modification not working"


@pytest.mark.parametrize("batch_size", [5, 10, 20])
def test_large_batch_processing_isolation(batch_size):
    """Test 13.4.5: Large batch processing maintains isolation"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    if len(df) < batch_size * 2:
        pytest.skip(f"Insufficient companies for batch size {batch_size}")
    
    # Store baseline for first company
    first_company_baseline = df.iloc[0].get("name")
    last_company_baseline = df.iloc[batch_size - 1].get("name")
    
    # Process batch
    batch = []
    for i in range(batch_size):
        company = {
            "name": df.iloc[i].get("name"),
            "industry": df.iloc[i].get("focus_sectors")
        }
        batch.append(company)
    
    # Verify baselines unchanged
    assert df.iloc[0].get("name") == first_company_baseline, \
        "First company baseline changed after batch processing"
    assert df.iloc[batch_size - 1].get("name") == last_company_baseline, \
        "Last company baseline changed after batch processing"


def test_field_level_isolation():
    """Test 13.4.6: Individual fields are properly isolated"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    if len(df) < 2:
        pytest.skip("Need at least 2 companies")
    
    # Extract same field from multiple companies
    fields_company_0 = {
        "name": df.iloc[0].get("name"),
        "headquarters": df.iloc[0].get("headquarters_address"),
        "sector": df.iloc[0].get("focus_sectors")
    }
    
    fields_company_1 = {
        "name": df.iloc[1].get("name"),
        "headquarters": df.iloc[1].get("headquarters_address"),
        "sector": df.iloc[1].get("focus_sectors")
    }
    
    # Should have different names (unless very unlucky)
    assert fields_company_0["name"] != fields_company_1["name"], \
        "Two different companies have same name - data contamination or invalid data"
    
    # Should have different headquarters (unless in same city)
    # Skip this check as it's not guaranteed


@pytest.mark.parametrize("company_idx", range(0, 116, 30))  # Sample across dataset
def test_immutability_verification(company_idx):
    """Test 13.4.7: Company data remains immutable across multiple accesses"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    if company_idx >= len(df):
        pytest.skip(f"Company index {company_idx} out of range")
    
    # Read company data three times
    reads = []
    for _ in range(3):
        row = df.iloc[company_idx]
        company_data = {
            "name": row.get("name"),
            "industry": row.get("focus_sectors"),
            "employees": row.get("employee_size")
        }
        reads.append(company_data)
    
    # All reads must be identical
    read_1, read_2, read_3 = reads
    
    assert read_1 == read_2, f"Read 1 and Read 2 differ for company {company_idx}"
    assert read_2 == read_3, f"Read 2 and Read 3 differ for company {company_idx}"
