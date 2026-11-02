
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = PROJECT_ROOT / "data" / "chronos_x_events.csv"

PARADOX_DATA_PATH = (
    PROJECT_ROOT / "data" / "paradox_protocol" / "cx006_events.csv"
)

OUTPUT_PATH = PROJECT_ROOT / "data" / "m6_detection_results.csv"


def load_data():

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Main dataset not found: {DATA_PATH}"
        )

    if not PARADOX_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Paradox dataset not found: {PARADOX_DATA_PATH}"
        )

    main_df = pd.read_csv(DATA_PATH)
    paradox_df = pd.read_csv(PARADOX_DATA_PATH)

    df = pd.concat(
        [main_df, paradox_df],
        ignore_index=True
    )

    required = [
        "scenario_id", "event_id", "event_time",
        "arrival_time", "source", "event_type",
        "value", "trust_score", "signature_valid"
    ]

    missing = [
        col for col in required
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    df["scenario_id"] = (
        df["scenario_id"].astype(str).str.strip()
    )

    print("Main dataset loaded:", len(main_df))
    print("CX-006 Paradox dataset loaded:", len(paradox_df))
    print("Total events:", len(df))

    return df


def detect_attacks(df):

    df = df.copy()

    df["trust_score"] = pd.to_numeric(
        df["trust_score"], errors="coerce"
    )

    df["event_time"] = pd.to_datetime(
        df["event_time"], errors="coerce"
    )

    df["arrival_time"] = pd.to_datetime(
        df["arrival_time"], errors="coerce"
    )

    df["value_numeric"] = pd.to_numeric(
        df["value"], errors="coerce"
    )

    df["signature_text"] = (
        df["signature_valid"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["suspicious_reasons"] = ""

    # 1. Low-trust events
    low_trust = df["trust_score"] < 0.6

    df.loc[
        low_trust, "suspicious_reasons"
    ] += "Low trust score; "

    # 2. Invalid signatures
    invalid_signature = df["signature_text"].isin(
        ["false", "0", "no", "invalid"]
    )

    df.loc[
        invalid_signature, "suspicious_reasons"
    ] += "Invalid signature; "

    # 3. Duplicate or replayed event IDs
    duplicate_events = df.duplicated(
        subset=["scenario_id", "event_id"],
        keep=False
    )

    df.loc[
        duplicate_events, "suspicious_reasons"
    ] += "Duplicate event ID; "

    # 4. Delayed messages
    delay = (
        df["arrival_time"] - df["event_time"]
    ).dt.total_seconds()

    df["arrival_delay_seconds"] = delay

    delayed = delay > 60

    df.loc[
        delayed, "suspicious_reasons"
    ] += "Delayed message; "

    # 5. Numerical outliers using IQR
    for (scenario, event_type), group in df.groupby(
        ["scenario_id", "event_type"]
    ):

        values = group["value_numeric"].dropna()

        if len(values) < 8:
            continue

        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)

        iqr = q3 - q1

        if iqr == 0:
            continue

        lower_limit = q1 - 1.5 * iqr
        upper_limit = q3 + 1.5 * iqr

        unusual = (
            (group["value_numeric"] < lower_limit)
            | (group["value_numeric"] > upper_limit)
        )

        df.loc[
            group.index[unusual],
            "suspicious_reasons"
        ] += "Unusual sensor value; "

    # 6. Assign detection status
    df["detection_status"] = "NO_FLAG"

    flagged = df["suspicious_reasons"] != ""

    df.loc[
        flagged, "detection_status"
    ] = "REVIEW_REQUIRED"

    df["review_priority"] = "LOW"

    df.loc[
        flagged, "review_priority"
    ] = "MEDIUM"

    # HIGH priority for invalid signatures or duplicates
    high_priority = (
        invalid_signature | duplicate_events
    ) & flagged

    df.loc[
        high_priority, "review_priority"
    ] = "HIGH"

    return df


def print_report(results):

    print("\n========== M6 ATTACK DETECTION REPORT ==========")

    for scenario_id, group in results.groupby("scenario_id"):

        flagged = group[
            group["detection_status"] == "REVIEW_REQUIRED"
        ]

        high = group[
            group["review_priority"] == "HIGH"
        ]

        print(f"\nScenario: {scenario_id}")
        print(f"Total events: {len(group)}")
        print(f"Events requiring review: {len(flagged)}")
        print(f"High-priority events: {len(high)}")

        if not flagged.empty:

            print("\nSuspicious signals:")

            for _, row in flagged.iterrows():

                print(
                    f"- Event {row['event_id']} | "
                    f"Source: {row['source']} | "
                    f"Priority: {row['review_priority']} | "
                    f"Reason: {row['suspicious_reasons']}"
                )

    print("\nNOTE: Flags indicate suspicious signals only.")
    print("They do not prove that an attack occurred.")


def main():

    print("\nLoading CHRONOS-X datasets...")

    df = load_data()

    results = detect_attacks(df)

    print_report(results)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    results.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(
        f"\nDetailed results saved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
