from pathlib import Path
import pandas as pd


def load_events(file_path):
    data = pd.read_csv(file_path)

    required = [
        "scenario_id", "event_id", "event_time",
        "arrival_time", "source", "event_type",
        "trust_score", "component_id", "signature_valid"
    ]

    missing = [col for col in required if col not in data.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    data["event_time"] = pd.to_datetime(
        data["event_time"], errors="coerce"
    )

    data["arrival_time"] = pd.to_datetime(
        data["arrival_time"], errors="coerce"
    )

    data["trust_score"] = pd.to_numeric(
        data["trust_score"], errors="coerce"
    ).fillna(0.5).clip(0, 1)

    data["signature_valid"] = (
        data["signature_valid"]
        .astype(str).str.lower()
        .isin(["true", "1", "yes"])
    )

    return data


def reconstruct_scenario(data):

    original_count = len(data)

    data = data.sort_values("arrival_time").copy()

    data = data.drop_duplicates(
        subset=["scenario_id", "event_id"],
        keep="first"
    ).copy()

    duplicates = original_count - len(data)

    data["confidence"] = (
        data["trust_score"] * 0.7
        + data["signature_valid"].astype(float) * 0.3
    )

    data["reconciliation_status"] = data.apply(
        lambda row: (
            "REVIEW_REQUIRED"
            if row["confidence"] < 0.6
            else "ACCEPTED"
        ),
        axis=1
    )

    data["arrival_delay_seconds"] = (
        data["arrival_time"] - data["event_time"]
    ).dt.total_seconds()

    data["timing_status"] = data["arrival_delay_seconds"].apply(
        lambda delay: (
            "INVALID_TIME"
            if pd.isna(delay) or delay < 0
            else "DELAYED"
            if delay > 0
            else "ON_TIME"
        )
    )

    event_history = data.sort_values(
        ["event_time", "arrival_time", "event_id"]
    ).reset_index(drop=True)

    arrival_history = data.sort_values(
        ["arrival_time", "event_time", "event_id"]
    ).reset_index(drop=True)

    return event_history, arrival_history, duplicates


def main():

    root = Path(__file__).resolve().parents[2]
    dataset_path = root / "data" / "chronos_x_events.csv"

    data = load_events(dataset_path)

    print("\n========== CHRONOS-X M1 ==========")

    total_duplicates = 0
    reconstructed_scenarios = {}

    for scenario_id, scenario_data in data.groupby("scenario_id"):

        event_history, arrival_history, duplicates = (
            reconstruct_scenario(scenario_data)
        )

        reconstructed_scenarios[scenario_id] = (
            event_history, arrival_history
        )

        total_duplicates += duplicates

        review_count = (
            event_history["reconciliation_status"]
            == "REVIEW_REQUIRED"
        ).sum()

        delayed_count = (
            event_history["timing_status"] == "DELAYED"
        ).sum()

        invalid_time_count = (
            event_history["timing_status"] == "INVALID_TIME"
        ).sum()

        print(f"\n--- Scenario: {scenario_id} ---")
        print("Input events:", len(scenario_data))
        print("Duplicates removed:", duplicates)
        print("Events requiring review:", review_count)
        print("Delayed messages:", delayed_count)
        print("Invalid timing records:", invalid_time_count)

        print("\nEvent-time history (first 5):")

        print(
            event_history[
                ["event_id", "event_time", "arrival_time",
                 "event_type", "source", "confidence",
                 "timing_status", "reconciliation_status"]
            ].head(5).to_string(index=False)
        )

        print("\nArrival-time alternative history (first 5):")

        print(
            arrival_history[
                ["event_id", "arrival_time", "event_type", "source"]
            ].head(5).to_string(index=False)
        )

    print("\n========== M1 SUMMARY ==========")
    print("Total input events:", len(data))
    print("Total scenarios:", data["scenario_id"].nunique())
    print("Total duplicates removed:", total_duplicates)
    print("Total reconstructed events:", sum(
        len(result[0]) for result in reconstructed_scenarios.values()
    ))

    print("\nM1 SCENARIO-WISE RECONSTRUCTION COMPLETED")


if __name__ == "__main__":
    main()
