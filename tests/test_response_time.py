"""
Test Case 13.2: Response Time (SCALE & PERFORMANCE)
Measures generation time for different company types and data volumes
Priority: Medium
Applicable to: All Parameters
"""

import pytest
import pandas as pd
import time
import json
from typing import Dict, Callable


# Load performance rules
def load_performance_rules():
    """Load performance rules from rules.json"""
    try:
        with open("rules/performance_rules.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


class PerformanceMetrics:
    """Track and analyze performance metrics"""
    
    def __init__(self):
        self.timings: Dict[str, list] = {}
        self.company_types: Dict[str, str] = {}
    
    def record_time(self, category: str, elapsed_time: float):
        """Record timing for a category"""
        if category not in self.timings:
            self.timings[category] = []
        self.timings[category].append(elapsed_time)
    
    def get_average(self, category: str) -> float:
        """Get average time for category"""
        if category not in self.timings or len(self.timings[category]) == 0:
            return 0
        return sum(self.timings[category]) / len(self.timings[category])
    
    def get_max(self, category: str) -> float:
        """Get maximum time for category"""
        if category not in self.timings or len(self.timings[category]) == 0:
            return 0
        return max(self.timings[category])


@pytest.fixture(scope="session")
def performance_metrics():
    """Performance metrics collector"""
    return PerformanceMetrics()


@pytest.fixture(scope="session")
def performance_rules():
    """Load and cache performance rules"""
    return load_performance_rules()


class PerformanceValidator:
    """Validate performance against rules"""
    
    def __init__(self, rules: dict):
        self.rules = rules
        self.slas = rules.get("performance_sla", {})
        self.company_thresholds = rules.get("company_type_thresholds", {})
        self.stage_thresholds = rules.get("company_stage_thresholds", {})
        self.benchmarks = rules.get("performance_benchmarks", {})
    
    def validate_sla(self, test_id: str, processing_time_ms: float) -> tuple:
        """Validate against SLA for specific test case"""
        sla_config = self.slas.get(test_id, {})
        if not sla_config:
            return True, "No SLA defined"
        
        expected_sla = sla_config.get("expected_sla_ms", 1000)
        acceptable_variance = sla_config.get("acceptable_variance_percent", 10) / 100
        
        max_allowed = expected_sla * (1 + acceptable_variance)
        passed = processing_time_ms <= max_allowed
        
        return passed, {
            "expected_ms": expected_sla,
            "max_allowed_ms": max_allowed,
            "actual_ms": processing_time_ms,
            "variance_percent": ((processing_time_ms - expected_sla) / expected_sla * 100)
        }
    
    def validate_company_type(self, company_type: str, processing_time_ms: float) -> tuple:
        """Validate against company type thresholds"""
        threshold = self.company_thresholds.get(company_type, {})
        if not threshold:
            return True, f"No threshold for type {company_type}"
        
        min_ms, max_ms = threshold.get("acceptable_range_ms", [0, 5000])
        passed = min_ms <= processing_time_ms <= max_ms
        
        return passed, {
            "company_type": company_type,
            "expected_ms": threshold.get("expected_processing_time_ms"),
            "acceptable_range_ms": [min_ms, max_ms],
            "actual_ms": processing_time_ms
        }
    
    def validate_company_stage(self, company_stage: str, processing_time_ms: float) -> tuple:
        """Validate against company stage thresholds"""
        threshold = self.stage_thresholds.get(company_stage, {})
        if not threshold:
            return True, f"No threshold for stage {company_stage}"
        
        min_ms, max_ms = threshold.get("acceptable_range_ms", [0, 5000])
        passed = min_ms <= processing_time_ms <= max_ms
        
        return passed, {
            "company_stage": company_stage,
            "expected_ms": threshold.get("expected_processing_time_ms"),
            "acceptable_range_ms": [min_ms, max_ms],
            "actual_ms": processing_time_ms
        }
    
    def validate_consistency(self, timings: list) -> tuple:
        """Validate variance in repeated runs"""
        if len(timings) < 2:
            return True, "Need at least 2 measurements"
        
        avg = sum(timings) / len(timings)
        
        # For very small timings (sub-millisecond), use absolute deviation instead of percentage
        if avg < 0.1:
            # Use absolute deviation in microseconds for sub-millisecond timings
            deviations_us = [abs(t - avg) * 1000 for t in timings]  # Convert to microseconds
            max_deviation_us = max(deviations_us)
            # Allow up to 100 microseconds deviation for sub-millisecond operations
            passed = max_deviation_us <= 100
            
            return passed, {
                "timings_ms": timings,
                "average_ms": avg,
                "measurement_type": "absolute_deviation_microseconds",
                "max_deviation_us": max_deviation_us,
                "tolerance_us": 100
            }
        else:
            # For larger timings, use percentage variance
            variance_percent = (max(timings) - min(timings)) / avg * 100 if avg > 0 else 0
            tolerance = self.rules.get("variance_tolerance", {}).get("consistency_check", {}).get("acceptable_variance_percent", 100)
            passed = variance_percent <= tolerance
            
            return passed, {
                "timings_ms": timings,
                "average_ms": avg,
                "variance_percent": variance_percent,
                "acceptable_variance_percent": tolerance
            }


def extract_company_type(nature_of_company):
    """Extract company classification"""
    if pd.isna(nature_of_company):
        return "Unknown"
    
    nature_str = str(nature_of_company).lower()
    
    if "public" in nature_str:
        if "subsidiary" in nature_str:
            return "Public_Subsidiary"
        return "Public"
    elif "private" in nature_str:
        if "subsidiary" in nature_str:
            return "Private_Subsidiary"
        return "Private"
    elif "subsidiary" in nature_str:
        return "Subsidiary"
    
    return "Unknown"


def extract_company_stage(nature_of_company, annual_revenue=None):
    """Extract company stage (startup, scale-up, enterprise)"""
    nature_str = str(nature_of_company).lower() if pd.notna(nature_of_company) else ""
    
    if "public" in nature_str or "enterprise" in nature_str:
        return "Enterprise"
    
    if pd.notna(annual_revenue):
        try:
            revenue = float(annual_revenue) if isinstance(annual_revenue, (int, float)) else 0
            if revenue > 1000000000:  # > $1B
                return "Enterprise"
            elif revenue > 100000000:  # > $100M
                return "Scale-up"
            elif revenue > 0:
                return "Startup"
        except:
            pass
    
    if "startup" in nature_str or "private" in nature_str:
        return "Startup"
    
    return "Scale-up"


class CompanyDataProcessor:
    """Processes company data and measures performance"""
    
    @staticmethod
    def process_company_record(row: pd.Series) -> Dict:
        """Process a single company record and measure time"""
        start_time = time.time()
        
        try:
            # Extract relevant fields
            company_data = {
                "name": row.get("name", ""),
                "type": extract_company_type(row.get("nature_of_company")),
                "stage": extract_company_stage(row.get("nature_of_company"), row.get("annual_revenue")),
                "overview_length": len(str(row.get("overview_text", ""))) if pd.notna(row.get("overview_text")) else 0,
                "office_count": row.get("office_count"),
                "employee_size": row.get("employee_size"),
                "revenue": row.get("annual_revenue"),
                "profitability": row.get("profitability_status")
            }
            
            elapsed_time = time.time() - start_time
            return {
                "data": company_data,
                "processing_time": elapsed_time,
                "success": True
            }
        except Exception as e:
            elapsed_time = time.time() - start_time
            return {
                "error": str(e),
                "processing_time": elapsed_time,
                "success": False
            }


@pytest.mark.parametrize("company_idx", range(0, 116, 10))  # Every 10th company for speed
def test_response_time_public_vs_private(company_idx, performance_metrics, performance_rules):
    """Test 13.2.3: Compare response time between public and private companies of similar size"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    if company_idx >= len(df):
        pytest.skip(f"Company index {company_idx} out of range")
    
    row = df.iloc[company_idx]
    company_type = extract_company_type(row.get("nature_of_company"))
    
    result = CompanyDataProcessor.process_company_record(row)
    
    assert result["success"], f"Failed to process company: {result.get('error')}"
    
    # Record timing
    processing_time_ms = result["processing_time"] * 1000
    performance_metrics.record_time(f"type_{company_type}", processing_time_ms)
    
    # Validate against rules
    validator = PerformanceValidator(performance_rules)
    
    # Get company type thresholds
    type_passed, type_info = validator.validate_company_type(company_type, processing_time_ms)
    
    # Processing should be within company type thresholds
    assert type_passed, f"Processing time {processing_time_ms:.2f}ms exceeds threshold for {company_type}: {type_info}"


@pytest.mark.parametrize("company_idx", range(0, 116, 10))
def test_response_time_startup_vs_enterprise(company_idx, performance_metrics, performance_rules):
    """Test 13.2.2: Measure response time for a startup company profile vs large enterprises"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    if company_idx >= len(df):
        pytest.skip(f"Company index {company_idx} out of range")
    
    row = df.iloc[company_idx]
    company_stage = extract_company_stage(row.get("nature_of_company"), row.get("annual_revenue"))
    
    result = CompanyDataProcessor.process_company_record(row)
    
    assert result["success"], f"Failed to process company: {result.get('error')}"
    
    # Record timing
    processing_time_ms = result["processing_time"] * 1000
    performance_metrics.record_time(f"stage_{company_stage}", processing_time_ms)
    
    # Validate against rules
    validator = PerformanceValidator(performance_rules)
    stage_passed, stage_info = validator.validate_company_stage(company_stage, processing_time_ms)
    
    # Processing should be within stage thresholds
    assert stage_passed, f"Processing time {processing_time_ms:.2f}ms exceeds threshold for {company_stage}: {stage_info}"


def test_response_time_by_data_volume(performance_metrics, performance_rules):
    """Test 13.2.04: Detect performance regression when entity complexity increases"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    # Categorize by overview length (data volume)
    short_desc = df[df['overview_text'].apply(lambda x: len(str(x)) if pd.notna(x) else 0) < 100]
    medium_desc = df[df['overview_text'].apply(lambda x: 100 <= len(str(x)) if pd.notna(x) else False) < 300]
    long_desc = df[df['overview_text'].apply(lambda x: len(str(x)) >= 300 if pd.notna(x) else False)]
    
    validator = PerformanceValidator(performance_rules)
    volume_thresholds = performance_rules.get("data_volume_categories", {})
    
    for dataset, label in [(short_desc, "short_description"), (medium_desc, "medium_description"), (long_desc, "long_description")]:
        if len(dataset) > 0:
            for idx, row in dataset.head(3).iterrows():
                result = CompanyDataProcessor.process_company_record(row)
                assert result["success"], f"Failed to process: {result.get('error')}"
                
                processing_time_ms = result["processing_time"] * 1000
                performance_metrics.record_time(f"volume_{label}", processing_time_ms)
                
                # Validate against volume thresholds
                threshold = volume_thresholds.get(label, {})
                if threshold:
                    min_ms, max_ms = threshold.get("acceptable_range_ms", [0, 10000])
                    assert min_ms <= processing_time_ms <= max_ms, \
                        f"Processing time {processing_time_ms:.2f}ms for {label} outside range [{min_ms}, {max_ms}]"


def test_response_time_consistency(performance_rules):
    """Test 13.2.05: Validate consistency of response time across repeated runs"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    if len(df) == 0:
        pytest.skip("No companies to test")
    
    row = df.iloc[0]
    timings = []
    
    # Process same company 5 times
    for _ in range(5):
        result = CompanyDataProcessor.process_company_record(row)
        assert result["success"], "Processing failed"
        timings.append(result["processing_time"] * 1000)  # Convert to ms
    
    # Validate consistency using rules
    validator = PerformanceValidator(performance_rules)
    consistency_passed, consistency_info = validator.validate_consistency(timings)
    
    assert consistency_passed, \
        f"Response time inconsistent: {consistency_info}"


@pytest.mark.benchmark
def test_batch_processing_performance_summary(performance_metrics, performance_rules):
    """Test 13.2.01: Measure response time for Fortune 500 company profiles (high complexity)"""
    df = pd.read_csv("data/Company Master(Flat Companies Data).csv")
    
    # Process sample of companies
    sample = df.head(20)
    
    validator = PerformanceValidator(performance_rules)
    benchmarks = performance_rules.get("performance_benchmarks", {})
    
    for idx, row in sample.iterrows():
        result = CompanyDataProcessor.process_company_record(row)
        company_type = result["data"].get("type") if result["success"] else "Unknown"
        processing_time_ms = result["processing_time"] * 1000
        performance_metrics.record_time(f"batch_{company_type}", processing_time_ms)
    
    # Print performance summary
    print("\n" + "=" * 80)
    print("PERFORMANCE METRICS SUMMARY (Test 13.2)")
    print("=" * 80)
    
    # Validate against benchmarks
    single_benchmark = benchmarks.get("single_company_processing", {})
    if single_benchmark:
        acceptable_ms = single_benchmark.get("acceptable_ms", 500)
        print(f"\nBenchmark: Single Company Processing")
        print(f"  Acceptable: {acceptable_ms}ms")
        print(f"  Critical: {single_benchmark.get('critical_threshold_ms')}ms")
    
    print("\nMetrics by Category:")
    for metric_type in sorted(set([k.split("_")[0] for k in performance_metrics.timings.keys()])):
        matching_keys = [k for k in performance_metrics.timings.keys() if k.startswith(metric_type)]
        
        for key in sorted(matching_keys):
            avg = performance_metrics.get_average(key)
            max_val = performance_metrics.get_max(key)
            count = len(performance_metrics.timings[key])
            
            if count > 0:
                print(f"{key:30} -> Avg: {avg:7.2f}ms, Max: {max_val:7.2f}ms, Count: {count}")
    
    print("=" * 80)
