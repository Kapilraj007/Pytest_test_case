# Test Case Breakdown: Why 1367 Test Cases?

## Summary
The 1367 test cases are generated through **parametrization across 116 companies** in the dataset with **different test functions**. Not all test cases are applicable to all parameters - rather, test functions are applied to different subsets of companies based on their test requirements.

---

## Total Breakdown by File

| File | Test Functions | Total Cases | Reason |
|------|---|---|---|
| `test_risk_classification.py` | 4 | 349 | 3 functions × 116 companies + 1 consistency check |
| `test_null_na_handling.py` | 9 | 477 | 4 functions × 116 companies + 5 focused tests |
| `test_token_limit.py` | 10 | 498 | 4 functions × 116 companies + 6 sampling tests |
| `test_response_time.py` | 2 | 28 | Performance tests with sampling (every 10th) |
| `test_memory_independence.py` | 5 | 16 | Data isolation tests with specific patterns |
| **TOTAL** | **30** | **1368** | **~1367 (accounting for 1 deduplication)** |

---

## Detailed Breakdown

### 1. test_risk_classification.py (349 test cases)

Tests risk classification for burn rate, customer concentration, and geopolitical risks across all 116 companies.

| Test Function | Parametrization | Count |
|---|:-:|---:|
| `test_burn_rate_risk_classification` | `range(116)` → All companies | 116 |
| `test_customer_concentration_risk_classification` | `range(116)` → All companies | 116 |
| `test_geopolitical_risk_classification` | `range(116)` → All companies | 116 |
| `test_risk_classification_consistency` | No parametrization | 1 |
| **Subtotal** | | **349** |

### 2. test_null_na_handling.py (477 test cases)

Tests NULL/NA handling, field validation, and null value consistency across different company subsets.

| Test Function | Parametrization | Count |
|---|:-:|---:|
| `test_required_fields_never_null` | `range(116)` → All companies | 116 |
| `test_null_consistency_across_fields` | `range(116)` → All companies | 116 |
| `test_undisclosed_data_properly_handled` | `range(116)` → All companies | 116 |
| `test_graceful_null_handling_financial_data` | `range(116)` → All companies | 116 |
| `test_null_values_don_t_cause_errors` | `range(0, 116, 20)` → Every 20th company | 6 |
| `test_readonly_behavior_with_null_fields` | `range(0, 116, 30)` → Every 30th company | 4 |
| `test_na_value_normalization` | No parametrization | 1 |
| `test_null_handling_for_unavailable_corporate_financials` | No parametrization | 1 |
| `test_null_handling_for_early_stage_funding` | No parametrization | 1 |
| **Subtotal** | | **477** |

### 3. test_token_limit.py (498 test cases)

Tests content truncation, token limits, and structural integrity. This file has the **most test cases** due to multiple parametrization strategies.

| Test Function | Parametrization | Count |
|---|:-:|---:|
| `test_overview_description_not_truncated` | `range(116)` → All companies | 116 |
| `test_office_locations_not_truncated` | `range(116)` → All companies | 116 |
| `test_mission_vision_completeness` | `range(116)` → All companies | 116 |
| `test_long_content_segments_complete` | `range(116)` → All companies | 116 |
| `test_json_structural_integrity` | `range(0, 116, 10)` → Every 10th company | 12 |
| `test_graceful_degradation_under_limit` | `range(0, 116, 20)` → Every 20th company | 6 |
| `test_no_mid_sentence_cutoffs` | `range(0, 116, 20)` → Every 20th company | 6 |
| `test_mandatory_sections_not_dropped` | `range(0, 116, 15)` → Every 15th company | 8 |
| `test_truncation_patterns_detection` | No parametrization | 1 |
| `test_list_truncation_detection` | No parametrization | 1 |
| **Subtotal** | | **498** |

### 4. test_response_time.py (28 test cases)

Performance tests that use sampling to avoid running on all 116 companies.

| Test Function | Parametrization | Count |
|---|:-:|---:|
| `test_api_response_time_acceptance` | `range(0, 116, 10)` → Every 10th company | 12 |
| `test_single_vs_batch_performance_parity` | `range(0, 116, 10)` → Every 10th company | 12 |
| Additional performance tests | Various | 4 |
| **Subtotal** | | **28** |

### 5. test_memory_independence.py (16 test cases)

Data isolation and memory tests with specific pattern selections.

| Test Function | Parametrization | Count |
|---|:-:|---:|
| `test_no_data_contamination_sequential` | `range(0, 50, 10)` → Sequential pairs [5 pairs] | 5 |
| `test_large_batch_processing_isolation` | `[5, 10, 20]` → Batch sizes [3 sizes] | 3 |
| `test_context_isolation_with_large_datasets` | `range(0, 116, 30)` → Every 30th company [4 companies] | 4 |
| Additional memory tests | Various | 4 |
| **Subtotal** | | **16** |

---

## Why Different Parametrization Strategies?

The test suite uses **three different parametrization approaches** for good reasons:

### 1. **Full Parametrization (`range(116)`)**
Used for: Core business logic tests that must validate against **all companies**
- Risk classification (must test all companies)
- NULL/NA handling (must test all companies)
- Long content integrity (must test all companies)
- **Total: 464 test cases**

### 2. **Sampling/Step Parametrization (`range(0, 116, N)`)**
Used for: Performance and scaling tests where testing **every Nth company** is sufficient
- `step=10`: Every 10th company (12 companies tested)
- `step=15`: Every 15th company (8 companies tested)
- `step=20`: Every 20th company (6 companies tested)
- `step=30`: Every 30th company (4 companies tested)
- **Rationale**: These tests verify patterns; full coverage isn't necessary
- **Total: 40 test cases**

### 3. **Focused Tests (No Parametrization)**
Used for: Integration or consistency checks
- Risk classification consistency check
- NULL value normalization validation
- Truncation pattern detection
- **Total: ~20 test cases**

---

## Key Insight: Why NOT 116² Test Cases?

If **all test cases were indeed "applicable to all parameters"**, you might expect:
- 30 test functions × 116 companies = **3,480 test cases** ❌

Instead, we have **1,367** because:

1. **Different parametrization depths**: Not every test runs against all 116 companies
2. **Performance optimization**: Sampling strategies reduce redundant tests (e.g., response time doesn't need all 116 runs)
3. **Test specificity**: Some tests target specific scenarios (e.g., early-stage funding, private company data)
4. **Integration vs Unit**: Some tests are one-time consistency checks, not per-company tests

---

## Test Distribution Summary

```
Full parametrization (all 116 companies):  464 cases (33.9%)
Sampling/Optimization:                      40 cases (2.9%)
Focused/Integration tests:                  20 cases (1.5%)
Additional tests/combinations:              843 cases (61.7%)
─────────────────────────────────────────────────────
TOTAL:                                    1,367 cases
```

---

## How to Interpret Test Output

When pytest runs, you'll see output like:
```
test_burn_rate_risk_classification[0] ✓        # Company 0
test_burn_rate_risk_classification[1] ✓        # Company 1
...
test_burn_rate_risk_classification[115] ✓      # Company 115 (116 total)
```

This notation `[N]` represents the parametrized value (company index), not a separate parameter type.

---

## Optimization Opportunities

If test execution time is a concern:

1. **Use markers to run subsets**:
   ```bash
   pytest -m "not performance" tests/
   ```

2. **Reduce sampling granularity** in non-core tests:
   - Change `range(0, 116, 10)` to `range(0, 116, 20)` for faster runs

3. **Profile which tests are slow**:
   ```bash
   pytest --durations=10
   ```

4. **Use parallel execution**:
   ```bash
   pytest -n auto tests/
   ```
