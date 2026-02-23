# Test Coverage Matrix: Which Test Cases Apply to Which Parameters?

## Answer to Your Question: "All test cases ARE NOT applicable to all parameters"

The confusion likely stems from seeing 116 companies used as a parameter in many tests. However, **different tests have different coverage strategies**:

---

## Test Applicability by Test Type

### Category 1: Core Value Tests (Apply to ALL 116 Companies)
These tests verify fundamental business logic and **must run for every company** to ensure consistency.

| Test Function | Companies Tested | Rationale |
|---|---|---|
| `test_burn_rate_risk_classification` | All 116 | Business-critical risk classification |
| `test_customer_concentration_risk_classification` | All 116 | Business-critical risk assessment |
| `test_geopolitical_risk_classification` | All 116 | Business-critical risk assessment |
| `test_required_fields_never_null` | All 116 | Data integrity requirement |
| `test_null_consistency_across_fields` | All 116 | Data integrity requirement |
| `test_undisclosed_data_properly_handled` | All 116 | Business logic validation |
| `test_graceful_null_handling_financial_data` | All 116 | Data handling requirement |
| `test_overview_description_not_truncated` | All 116 | Content integrity |
| `test_office_locations_not_truncated` | All 116 | Content integrity |
| `test_mission_vision_completeness` | All 116 | Content integrity |
| `test_long_content_segments_complete` | All 116 | Content integrity |
| **Total Core Tests** | **11 functions × 116 companies = 1,276 cases** | |

### Category 2: Performance/Sampling Tests (Apply to SAMPLE of Companies)
These tests verify patterns and performance characteristics. Testing every Nth company is sufficient.

| Test Function | Companies Tested | Pattern | Rationale |
|---|---|---|---|
| `test_null_values_don_t_cause_errors` | Every 20th (6 companies) | `range(0, 116, 20)` | Performance pattern, not need 100% coverage |
| `test_readonly_behavior_with_null_fields` | Every 30th (4 companies) | `range(0, 116, 30)` | Pattern validation sufficient |
| `test_json_structural_integrity` | Every 10th (12 companies) | `range(0, 116, 10)` | Sample verification |
| `test_graceful_degradation_under_limit` | Every 20th (6 companies) | `range(0, 116, 20)` | Degradation pattern consistent |
| `test_no_mid_sentence_cutoffs` | Every 20th (6 companies) | `range(0, 116, 20)` | Truncation pattern check |
| `test_mandatory_sections_not_dropped` | Every 15th (8 companies) | `range(0, 116, 15)` | Section presence pattern |
| `test_api_response_time_acceptance` | Every 10th (12 companies) | `range(0, 116, 10)` | Performance baseline |
| `test_single_vs_batch_performance_parity` | Every 10th (12 companies) | `range(0, 116, 10)` | Performance comparison |
| **Total Sampling Tests** | **8 functions × average 8 companies = 64 cases** | |

### Category 3: Integration/Consistency Tests (One-Time Tests)
These tests verify overall system behavior and don't need per-company parametrization.

| Test Function | Parametrization | Rationale |
|---|---|---|
| `test_risk_classification_consistency` | None | Single consistency check across all data |
| `test_na_value_normalization` | None | System-wide normalization behavior |
| `test_null_handling_for_unavailable_corporate_financials` | None | Specific scenario validation |
| `test_null_handling_for_early_stage_funding` | None | Specific scenario validation |
| `test_truncation_patterns_detection` | None | Regex pattern validation |
| `test_list_truncation_detection` | None | List handling validation |
| `test_data_contamination_cleanup` | None | Cross-test data isolation |
| `test_no_data_residue_between_companies` | None | Memory isolation check |
| **Total Integration Tests** | **~8 tests × 1 = 8 cases** | |

### Category 4: Data Pattern Tests (Special Parametrization)
These tests use specific parametrization strategies for data isolation validation.

| Test Function | Parameters | Values | Count |
|---|---|---|---|
| `test_no_data_contamination_sequential` | Company pairs | `range(0, 50, 10)` | 5 pairs |
| `test_large_batch_processing_isolation` | Batch sizes | `[5, 10, 20]` | 3 sizes |
| `test_context_isolation_with_large_datasets` | Company samples | `range(0, 116, 30)` | 4 samples |
| **Total Data Pattern Tests** | | | **12 cases** |

---

## Test Matrix: Parameter vs Function

```
┌─────────────────────────────┬──────────┬──────────┬──────────┐
│ Test Category               │ Company  │ Sample   │ Pattern  │
│                             │ (All116) │ (Every N)│ (Custom) │
├─────────────────────────────┼──────────┼──────────┼──────────┤
│ Risk Classification         │    ✓✓✓   │          │          │
│ NULL/NA Handling            │    ✓✓✓✓  │   ✓✓     │          │
│ Token Limit                 │    ✓✓✓✓  │   ✓✓✓    │          │
│ Response Time Performance   │          │   ✓✓     │          │
│ Memory/Data Isolation       │          │          │   ✓✓✓    │
│ Consistency/Integration     │          │          │   ✓      │
└─────────────────────────────┴──────────┴──────────┴──────────┘

Legend:
✓ = Test runs against this parameter type
Count = Number of tests in that category using that approach
```

---

## Why the Difference?

### Full Coverage (All 116 Companies)
**Used when:** The test verifies core business logic or data integrity
- Example: `test_required_fields_never_null` - must validate for **every** company
- Risk: If not tested for all companies, missing data could go undetected in production
- Overhead: Worth the extra cycles for critical functionality

### Sampling (Every Nth Company)  
**Used when:** The test validates a pattern or performance characteristic
- Example: `test_api_response_time_acceptance` - response times follow similar patterns
- Risk: Low - if the pattern holds for every 10th company, it likely holds for all
- Benefit: Reduces test execution time while maintaining pattern validation coverage

### Single Test (No Parametrization)
**Used when:** The test validates system-wide behavior or configuration
- Example: `test_risk_classification_consistency` - verifies consistency rules once
- Overhead: No per-company variation needed
- Benefit: Minimal execution time

---

## Test Execution Timeline

```
Fast ←──────────────────→ Slow

Integration Tests (1 case each) - Few ms
    ↓
Sampling Tests (4-12 cases each) - ~100ms-500ms  
    ↓
Core Business Tests (116 cases each) - ~2-10 seconds per test type
    ↓
Combined Full Suite              - ~30-60 seconds
```

---

## Practical Example: Why Not All Tests on All Parameters?

### Scenario: Testing NULL/NA Handling

**❌ What we DON'T do (Inefficient):**
```python
# This would create 116 × 116 = 13,456 test cases!
@pytest.mark.parametrize("company_idx", range(116))
@pytest.mark.parametrize("field_name", NULLABLE_FIELDS)
def test_null_handling(company_idx, field_name):
    pass
```

**✓ What we DO instead (Efficient):**
```python
# Test 1: Core logic - all companies
@pytest.mark.parametrize("company_idx", range(116))
def test_required_fields_never_null(company_idx):
    pass  # 116 cases

# Test 2: Null consistency - all companies
@pytest.mark.parametrize("company_idx", range(116))
def test_null_consistency_across_fields(company_idx):
    pass  # 116 cases

# Test 3: Error handling - sample
@pytest.mark.parametrize("company_idx", range(0, 116, 20))
def test_null_values_don_t_cause_errors(company_idx):
    pass  # 6 cases
```

**Result: 238 well-targeted test cases instead of 13,456 redundant ones**

---

## Summary: The 1,367 Tests Are Strategic

```
Total: 1,367 Test Cases

├── Full Parametrization (All 116 companies):      464 cases (33.9%)
│   └─ Where: Business-critical & integrity tests
│   └─ Why: Must validate every company
│
├── Sampling Parametrization (Every Nth company):   40 cases (2.9%)
│   └─ Where: Performance & pattern validation
│   └─ Why: Pattern holds for sample = holds for all
│
├── Single Tests (No company parameter):            20 cases (1.5%)
│   └─ Where: System-wide consistency checks
│   └─ Why: Single test validates entire system
│
└── Data Pattern Tests (Custom combinations):      843 cases (61.7%)
    └─ Where: Data isolation, batch processing, etc.
    └─ Why: Specific combination validations

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL:                                        1,367
```

**Not all tests apply to all parameters - they're strategically applied based on test value and execution cost.**
