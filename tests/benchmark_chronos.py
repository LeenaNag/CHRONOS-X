
import sys
import time
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.pipeline import run_pipeline


SCENARIOS = [
    "CX-001",
    "CX-002",
    "CX-003",
    "CX-004",
    "CX-005",
    "CX-006"
]


def benchmark_scenario(scenario_id):
    start_time = time.perf_counter()

    result = run_pipeline(scenario_id)

    execution_time = time.perf_counter() - start_time

    return {
        "scenario_id": scenario_id,
        "execution_time_seconds": round(execution_time, 4),
        "events_analyzed": len(result["m1"]["event_history"]),
        "root_cause": result["m2"]["root_cause"],
        "best_simulated_option": result["m3"]["best_simulated_option"],
        "safety_status": result["m7"]["status"],
        "flagged_records": int(
            (
                result["m6"]["detection_status"]
                == "REVIEW_REQUIRED"
            ).sum()
        )
    }


def main():
    results = []

    print("\n========== CHRONOS-X BENCHMARK ==========\n")

    for scenario_id in SCENARIOS:
        try:
            result = benchmark_scenario(scenario_id)
            results.append(result)

            print(f"Scenario: {scenario_id}")
            print(f"Events: {result['events_analyzed']}")
            print(f"Execution time: {result['execution_time_seconds']} seconds")
            print(f"Root cause: {result['root_cause']}")
            print(f"Best simulated option: {result['best_simulated_option']}")
            print(f"Safety status: {result['safety_status']}")
            print(f"Flagged records: {result['flagged_records']}")
            print("-" * 45)

        except Exception as error:
            print(f"{scenario_id} failed: {error}")

    if not results:
        print("No benchmark results were generated.")
        return

    report = pd.DataFrame(results)

    output_directory = PROJECT_ROOT / "results"
    output_directory.mkdir(exist_ok=True)

    output_file = output_directory / "benchmark_summary.csv"
    report.to_csv(output_file, index=False)

    print("\n========== BENCHMARK SUMMARY ==========")
    print(f"Scenarios completed: {len(results)}/{len(SCENARIOS)}")
    print(
        "Average execution time:",
        round(report["execution_time_seconds"].mean(), 4),
        "seconds"
    )
    print(
        "Total events analyzed:",
        int(report["events_analyzed"].sum())
    )
    print(f"\nReport saved to: {output_file}")


if __name__ == "__main__":
    main()
