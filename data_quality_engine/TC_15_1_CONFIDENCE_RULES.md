# TC 15.1 – Confidence Level Rules

## Objective
Validate that inferred and verified data are assigned correct confidence levels.

## Rules

| Condition | Confidence Level | Estimated |
|------------|------------------|------------|
| LLM inferred | Low | True |
| SEC Filing | High | False |

## JSON Rule Source
rules/test_tc_15_1.json