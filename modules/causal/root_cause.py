
from pathlib import Path
import argparse
import pandas as pd
import networkx as nx


def load_data():

    root = Path(__file__).resolve().parents[2]
    path = root / "data" / "chronos_x_events.csv"

    data = pd.read_csv(path)

    data["event_time"] = pd.to_datetime(
        data["event_time"], errors="coerce"
    )

    data["trust_score"] = pd.to_numeric(
        data["trust_score"], errors="coerce"
    ).fillna(0.5)

    data["numeric_value"] = pd.to_numeric(
        data["value"], errors="coerce"
    )

    if "signature_valid" in data.columns:
        data["signature_valid"] = (
            data["signature_valid"]
            .astype(str)
            .str.lower()
            .isin(["true", "1", "yes"])
        )

    return data


def calculate_trend(data, event_type):

    records = data[
        data["event_type"] == event_type
    ].copy()

    records = records.dropna(
        subset=["numeric_value", "event_time"]
    ).sort_values("event_time")

    if len(records) < 4:
        return None

    count = max(1, len(records) // 4)

    first = records["numeric_value"].head(count).median()
    last = records["numeric_value"].tail(count).median()

    if first == 0:
        return None

    percentage_change = (
        (last - first) / abs(first)
    ) * 100

    return {
        "first": first,
        "last": last,
        "change": percentage_change
    }


# T2: Conflicting report detection
def detect_conflicting_reports(data):

    conflicts = []

    required = ["event_type", "value"]

    if not all(col in data.columns for col in required):
        return conflicts

    for event_type, records in data.groupby("event_type"):

        values = (
            records["value"]
            .dropna()
            .astype(str)
            .str.strip()
        )

        unique_values = values.unique()

        if len(unique_values) > 1:

            sources = []

            if "source" in records.columns:
                sources = (
                    records.loc[values.index, "source"]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )

            conflicts.append({
                "event_type": event_type,
                "reported_values": unique_values.tolist(),
                "sources": sources,
                "report_count": len(values)
            })

    return conflicts


# T3: Potential hidden confounder assessment
def assess_confounding_risk(data):

    findings = []

    if "event_type" not in data.columns:
        return findings

    event_types = set(
        data["event_type"].dropna().unique()
    )

    has_temperature = "temperature" in event_types
    has_coolant_flow = "coolant_flow" in event_types

    if not (has_temperature and has_coolant_flow):
        return findings

    possible_context_events = {
        "machine_load",
        "operating_load",
        "production_rate",
        "ambient_temperature"
    }

    available_context = (
        possible_context_events.intersection(event_types)
    )

    if not available_context:

        findings.append({
            "cause": "Potential unobserved confounding",
            "status": "POSSIBLE_NOT_CONFIRMED",
            "evidence": [
                "Temperature and coolant-flow observations are present",
                "Operating-condition variables are not available",
                "An unobserved factor may influence both measurements"
            ],
            "missing_variables": sorted(
                possible_context_events
            ),
            "assumptions": (
                "The available observations cannot establish "
                "whether temperature and coolant-flow changes "
                "share an unobserved cause."
            )
        })

    else:

        findings.append({
            "cause": "Potential operating-condition confounding",
            "status": "REQUIRES_FURTHER_ANALYSIS",
            "evidence": [
                "Temperature and coolant-flow observations are present",
                "Operating-condition events are available: "
                + ", ".join(sorted(available_context))
            ],
            "missing_variables": [],
            "assumptions": (
                "The available operating-condition variables "
                "should be examined before attributing the "
                "observed changes to cooling degradation."
            )
        })

    return findings


def investigate_scenario(data):

    graph = nx.DiGraph()
    hypotheses = []

    event_types = set(
        data["event_type"].dropna().unique()
    )

    def add_hypothesis(name, score, evidence, assumptions):

        if not evidence:
            return

        score = min(100, max(0, score))

        hypotheses.append({
            "cause": name,
            "score": score,
            "evidence": evidence,
            "assumptions": assumptions
        })

        cause_node = "CAUSE: " + name

        graph.add_node(
            cause_node,
            type="hypothesis"
        )

        for item in evidence:

            evidence_node = "EVIDENCE: " + item

            graph.add_node(
                evidence_node,
                type="observation"
            )

            graph.add_edge(
                cause_node,
                evidence_node
            )

    # Calculate event trends.
    temp = calculate_trend(data, "temperature")
    flow = calculate_trend(data, "coolant_flow")
    pressure = calculate_trend(data, "pressure")
    vibration = calculate_trend(data, "vibration")

    # --------------------------------------------------
    # T2: Conflicting cooling-system reports
    # --------------------------------------------------

    conflicts = detect_conflicting_reports(data)

    for conflict in conflicts:

        if conflict["event_type"] in [
            "cooling_status",
            "cooling_system_status"
        ]:

            evidence = [
                "Conflicting cooling-system reports detected",
                "Reported values: " + ", ".join(
                    conflict["reported_values"]
                ),
                "Number of reports: " + str(
                    conflict["report_count"]
                )
            ]

            if conflict["sources"]:

                evidence.append(
                    "Reporting sources: " + ", ".join(
                        conflict["sources"]
                    )
                )

            add_hypothesis(
                "Conflicting cooling-system reports",
                85,
                evidence,
                "Different sources report different cooling-system "
                "statuses. Independent validation is required."
            )

    # --------------------------------------------------
    # T3: Potential hidden confounder assessment
    # --------------------------------------------------

    confounding_findings = assess_confounding_risk(data)

    for finding in confounding_findings:

        add_hypothesis(
            finding["cause"],
            75,
            finding["evidence"],
            finding["assumptions"]
        )

    # --------------------------------------------------
    # Hypothesis 1: Cooling system degradation
    # --------------------------------------------------

    if temp and flow:

        if temp["change"] > 5 and flow["change"] < -10:

            evidence = [
                f"Temperature increased by {temp['change']:.1f}%",
                f"Coolant flow decreased by {abs(flow['change']):.1f}%"
            ]

            add_hypothesis(
                "Cooling system degradation",
                90,
                evidence,
                "Temperature and coolant-flow trends are assumed "
                "to be relevant indicators of cooling performance."
            )

    # --------------------------------------------------
    # Hypothesis 2: Sensor spoofing or configuration tampering
    # --------------------------------------------------

    if "temperature" in event_types:

        temp_records = data[
            data["event_type"] == "temperature"
        ]

        source_medians = (
            temp_records.groupby("source")["numeric_value"]
            .median()
            .dropna()
        )

        sensor_gap = (
            source_medians.max() - source_medians.min()
            if len(source_medians) >= 2 else 0
        )

        suspicious_records = temp_records[
            (temp_records["trust_score"] < 0.6)
            | (~temp_records["signature_valid"].astype(bool))
        ]

        config_events = data[
            data["event_type"] == "sensor_config_change"
        ]

        if sensor_gap > 8 and (
            len(suspicious_records) > 0
            or len(config_events) > 0
        ):

            evidence = [
                f"Temperature sensor median difference: {sensor_gap:.1f}",
                f"Low-trust or invalid-signature readings: "
                f"{len(suspicious_records)}"
            ]

            if len(config_events) > 0:

                evidence.append(
                    f"Sensor configuration events: {len(config_events)}"
                )

            add_hypothesis(
                "Temperature sensor spoofing or tampering",
                95,
                evidence,
                "Different temperature sources should measure "
                "comparable conditions; the discrepancy needs validation."
            )

    # --------------------------------------------------
    # Hypothesis 3: Network or control-system manipulation
    # --------------------------------------------------

    network_events = data[
        data["event_type"] == "network_alert"
    ]

    cooling_commands = data[
        data["event_type"] == "cooling_command"
    ]

    if len(network_events) > 0:

        evidence = [
            f"Network alerts detected: {len(network_events)}"
        ]

        if len(cooling_commands) > 0:

            commands = (
                cooling_commands["value"]
                .astype(str)
                .unique()
            )

            evidence.append(
                f"Cooling commands observed: {', '.join(commands)}"
            )

        add_hypothesis(
            "Network or control-system manipulation",
            88,
            evidence,
            "Network alerts may be related to control activity; "
            "the actual causal connection requires simulator validation."
        )

    # --------------------------------------------------
    # Hypothesis 4: Misleading maintenance report
    # --------------------------------------------------

    maintenance = data[
        data["event_type"] == "maintenance_status"
    ]

    if len(maintenance) > 0 and temp and flow:

        low_trust_maintenance = (
            maintenance["trust_score"].mean() < 0.6
        )

        reports_healthy = (
            maintenance["value"]
            .astype(str)
            .str.upper()
            .eq("HEALTHY")
            .any()
        )

        if (
            low_trust_maintenance
            and reports_healthy
            and temp["change"] > 5
            and flow["change"] < -10
        ):

            evidence = [
                "Maintenance report claims HEALTHY",
                "Maintenance report has low average trust",
                f"Temperature increased by {temp['change']:.1f}%",
                f"Coolant flow decreased by {abs(flow['change']):.1f}%"
            ]

            add_hypothesis(
                "Potentially misleading maintenance report",
                92,
                evidence,
                "The maintenance report may conflict with sensor trends; "
                "the actual equipment condition needs independent checking."
            )

    # --------------------------------------------------
    # Hypothesis 5: Mechanical degradation
    # --------------------------------------------------

    if vibration and vibration["change"] > 20:

        evidence = [
            f"Vibration increased by {vibration['change']:.1f}%"
        ]

        if pressure and pressure["change"] > 10:

            evidence.append(
                f"Pressure increased by {pressure['change']:.1f}%"
            )

        add_hypothesis(
            "Possible mechanical equipment degradation",
            78,
            evidence,
            "Increasing vibration may indicate mechanical changes; "
            "equipment-specific limits and inspection are required."
        )

    hypotheses.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return hypotheses, graph


def analyze(data, selected_scenario=None):

    if selected_scenario:

        selected_scenario = selected_scenario.upper()

        data = data[
            data["scenario_id"] == selected_scenario
        ].copy()

        if data.empty:

            raise ValueError(
                f"Scenario not found: {selected_scenario}"
            )

    scenario_ids = sorted(
        data["scenario_id"].unique()
    )

    print("\n========== CHRONOS-X M2 ==========")

    for scenario_id in scenario_ids:

        scenario_data = data[
            data["scenario_id"] == scenario_id
        ].copy()

        hypotheses, graph = investigate_scenario(
            scenario_data
        )

        print(f"\nSCENARIO: {scenario_id}")
        print("Events analyzed:", len(scenario_data))
        print("Causal graph nodes:", graph.number_of_nodes())
        print("Evidence relationships:", graph.number_of_edges())

        print("\nRANKED ROOT-CAUSE HYPOTHESES:")

        if not hypotheses:

            print("No supported hypothesis found.")
            print("System status: INSUFFICIENT EVIDENCE")

        for rank, item in enumerate(hypotheses, start=1):

            print(
                f"\n{rank}. {item['cause']}"
                f" | Evidence score: {item['score']}/100"
            )

            print("   Supporting evidence:")

            for evidence in item["evidence"]:
                print("   -", evidence)

            print("   Assumption:", item["assumptions"])

        if hypotheses:

            print("\nTop hypothesis:", hypotheses[0]["cause"])
            print("Status: HYPOTHESIS - NOT CONFIRMED")

    print("\nM2 ROOT-CAUSE INVESTIGATION COMPLETED")


def main():

    parser = argparse.ArgumentParser(
        description="CHRONOS-X Causal Investigation"
    )

    parser.add_argument(
        "--scenario",
        type=str,
        default=None,
        help="Analyze one scenario, e.g. CX-002"
    )

    args = parser.parse_args()

    data = load_data()

    if args.scenario:

        requested = args.scenario.upper()

        if requested not in set(data["scenario_id"]):

            available = sorted(
                data["scenario_id"].unique()
            )

            raise ValueError(
                f"Unknown scenario {requested}. "
                f"Available scenarios: {available}"
            )

    analyze(data, args.scenario)


if __name__ == "__main__":
    main()
