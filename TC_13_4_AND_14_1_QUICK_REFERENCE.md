# TC-13.4 & TC-14.1 Quick Reference Guide

## Test Case Quick Lookup

### TC-13.4: Context & Memory Isolation

| Test | Description | Input | Expected |
|------|-------------|-------|----------|
| **01** | Sequential companies | Request A → Request B | Zero contamination |
| **02** | High-context residual | Large complex company → Small company | No inherited detail |
| **03** | Same industry isolation | 5 similar fintech companies | Each uniquely accurate |
| **04** | Named entity contamination | Company A executives → Company B | No entity bleed |
| **05** | Alternating requests | A → B → A → B | Consistent per entity |
| **06** | Batch stress test | 20 similar companies | 98%+ uniqueness |

**Files**: 
- Rules: `rules/context_isolation_rules.json`
- Tests: `tests/test_memory_independence.py`
- Status: ✅ **16 tests PASSING**

---

### TC-14.1: Null/NA Handling

| Test | Description | Scenario | Handling |
|------|-------------|----------|----------|
| **01** | Unavailable financial data | Private company, no financials | NA / Unknown, no estimates |
| **02** | Undisclosed funding amounts | Known rounds, unknown amounts | Mark as "Undisclosed" |
| **03** | Null consistency | Multiple missing attributes | Single null token for all |
| **04** | Schema completeness | Missing data points | All keys present, null values |
| **05** | No hallucination | Private startup, no revenue | Explicit "Not Disclosed", no ranges |
| **06** | N/A vs Unknown distinction | Various scenarios | Context-aware differentiation |

**Files**:
- Rules: `rules/null_handling_rules.json`
- Tests: `tests/test_null_na_handling.py`
- Status: ✅ **477 tests PASSING**

---

## Null Representation Quick Reference

### Standard Null Tokens
```
N/A              → Field not applicable for this entity
Not Disclosed    → Data exists but not publicly available
Unknown          → Data not found or unavailable
```

### Examples by Company Type

**Public Company Financials**
```
Revenue: $5.2B
Profit: $1.1B
Market Cap: $250B
```

**Private Company Financials**
```
Revenue: Not Disclosed
Profit: Not Disclosed
Valuation: Not Disclosed
```

**Non-Profit Organization**
```
Revenue: $45.8M
Profit: N/A (not applicable)
Social Impact: ... [specific metrics]
```

**Early-Stage Startup**
```
Revenue: N/A (pre-revenue)
Burn Rate: Not Disclosed
Runway: Unknown
```

---

## Contamination Detection Levels

### None (✅ PASS)
- No overlap between Company A and Company B data
- Each company fields are independent
- Named entities don't appear in wrong companies

### Minor (⚠️ WARNING)
- <1% substring overlap
- Common structural phrases (allowed)
- Generic terms (allowed)

### Moderate (❌ FAIL)
- >1% content overlap
- Repeated phrases from precious company
- Fuzzy matching >70%

### Critical (❌ FAIL - HARD STOP)
- Exact field matches
- Named entity carryover
- Full sentence duplication

---

## Running Individual Tests

### TC-13.4 Specific Tests
```bash
# All memory isolation tests
pytest tests/test_memory_independence.py -v

# Specific test case
pytest tests/test_memory_independence.py::test_no_data_contamination_sequential -v

# With detailed output
pytest tests/test_memory_independence.py -vv --tb=short
```

### TC-14.1 Specific Tests
```bash
# All null handling tests
pytest tests/test_null_na_handling.py -v

# Private company null handling
pytest tests/test_null_na_handling.py::test_graceful_null_handling_financial_data -v

# Null consistency checks
pytest tests/test_null_na_handling.py::test_null_consistency_across_fields -v
```

### Combined TC-13.4 & TC-14.1
```bash
pytest tests/test_memory_independence.py tests/test_null_na_handling.py -v
```

---

## Key Files Reference

### Rules Files
| File | Test Category | Coverage | Size |
|------|---------------|----------|------|
| `context_isolation_rules.json` | TC-13.4 | 6 test cases | 360 lines |
| `null_handling_rules.json` | TC-14.1 | 6 test cases | 480 lines |

### Test Files
| File | Tests | Status | Categories |
|------|-------|--------|------------|
| `test_memory_independence.py` | 16 | ✅ PASS | TC-13.4 |
| `test_null_na_handling.py` | 477 | ✅ PASS | TC-14.1 |

---

## Pass Criteria Summary

### TC-13.4 (Isolation)
- ✅ Zero contamination tolerance
- ✅ 100% consistency for repeats
- ✅ 98%+ uniqueness in batches
- ✅ No fuzzy matches >85% from previous

### TC-14.1 (Null Handling)
- ✅ No numeric hallucination
- ✅ Single null token type
- ✅ 100% schema completeness
- ✅ No approximations or ranges
- ✅ Correct N/A vs Unknown distinction

---

## Integration Points

### For Developers
1. Load rules from JSON files
2. Use NullDataHandler and DataContaminationDetector classes
3. Validate output against rules before returning

### For QA
1. Run full suite: `pytest tests/ -v`
2. Check specific category: `pytest tests/test_memory_independence.py -v`
3. Review rule definitions in JSON files

### For DevOps
1. Add to CI/CD: `pytest tests/test_memory_independence.py tests/test_null_na_handling.py`
2. Set expected: 493 tests passing
3. Fail on: <100% pass rate or new errors

---

## Common Issues & Solutions

### Issue: Null Token Mismatch
**Problem**: Output uses "NA" sometimes and "Not Available" other times
**Solution**: Standardize to single token per rules, use NullDataHandler

### Issue: Contamination Detected in Batch
**Problem**: Company B shows data from similar Company A
**Solution**: Ensure deep copy of company objects, clear session state

### Issue: False Positive on Named Entities
**Problem**: Common names flagged as contamination (e.g., "John Smith")
**Solution**: Use fuzzy matching >85%, exclude common name lists

### Issue: Required Field Null
**Problem**: Name or Industry type is null
**Solution**: Check data quality in CSV, these should never be null

---

## Performance Baselines

### Test Execution Times
- TC-13.4: ~5 seconds (16 tests)
- TC-14.1: ~9 seconds (477 tests)
- Combined: ~14 seconds (493 tests)

### Expected Pass Rates
- TC-13.4: 100% (16/16)
- TC-14.1: 100% (477/477)
- Both: 100% (493/493)

---

## Support & Documentation

For detailed information, see:
- Full implementation: `TC_13_4_AND_14_1_IMPLEMENTATION_SUMMARY.md`
- Rule specifications: `rules/context_isolation_rules.json`
- Null handling specs: `rules/null_handling_rules.json`

Last Updated: February 23, 2026
