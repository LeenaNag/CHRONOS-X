
# CHRONOS-X Benchmark Report

## 1. Benchmark Overview

The CHRONOS-X central pipeline was evaluated using six synthetic industrial scenarios.

## 2. Benchmark Results

| Scenario | Events | Execution Time (seconds) | Flagged Records | Safety Status |
|---|---:|---:|---:|---|
| CX-001 | 97 | 0.3205 | 4 | PASS |
| CX-002 | 67 | 0.2460 | 19 | UNKNOWN |
| CX-003 | 50 | 0.2496 | 4 | UNKNOWN |
| CX-004 | 45 | 0.2443 | 3 | UNKNOWN |
| CX-005 | 67 | 0.2437 | 0 | PASS |
| CX-006 | 14 | 0.2927 | 3 | UNKNOWN |

## 3. Overall Performance

- Total scenarios: 6
- Successfully completed scenarios: 6
- Total events analyzed: 340
- Average execution time: 0.2661 seconds
- Total records flagged for review: 33
- Safety status PASS: 2 scenarios
- Safety status UNKNOWN: 4 scenarios

## 4. Observations

- All six scenarios completed successfully.
- CX-001 identified cooling system degradation.
- CX-002 generated the highest number of records requiring review.
- CX-003 identified possible network or control-system manipulation.
- CX-004 identified a potentially misleading maintenance report.
- CX-005 identified possible mechanical equipment degradation.
- CX-006 demonstrated the Paradox Protocol scenario.

## 5. Safety Interpretation

PASS indicates that the prototype's configured checks passed for that scenario.

UNKNOWN indicates that the available evidence was insufficient for a confident safety determination.

Neither status represents certification for real industrial operation.

## 6. Limitations

- All benchmark scenarios use synthetic data.
- Execution times were measured in one local environment.
- Results depend on the current implementation and simulation assumptions.
- The benchmark does not establish real-world detection accuracy.
- No controlled ablation experiment has been completed yet.

## 7. Conclusion

The CHRONOS-X prototype successfully processed all six synthetic scenarios and analyzed 340 events.

The average measured pipeline execution time was 0.2661 seconds.

Further controlled experiments are required to evaluate individual module contributions and compare alternative system configurations.
