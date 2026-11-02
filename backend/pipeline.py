
from pathlib import Path
import sys
import pandas as pd

# ==========================================
# CHRONOS-X CENTRAL PIPELINE
# M1 TO M7 + PARADOX PROTOCOL
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATA_PATH = PROJECT_ROOT / "data" / "chronos_x_events.csv"

PARADOX_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "paradox_protocol"
    / "cx006_events.csv"
)

# IMPORTANT:
# hidden_ground_truth.json is evaluation-only.
# It is NEVER loaded by this live pipeline.


# ==========================================
# IMPORT PROJECT MODULES
# ==========================================

from modules.temporal.reconstruction import (
    load_events,
    reconstruct_scenario
)

from modules.causal.root_cause import (
    investigate_scenario
)

from modules.simulation.future_simulator import (
    run_scenario_simulation
)

from modules.agents.orchestrator import (
    MultiAgentOrchestrator
)

from modules.optimization.risk_optimizer import (
    optimize_scenario
)

from modules.security.attack_detection import (
    detect_attacks
)

from modules.safety.verification import (
    build_plan_from_m5,
    verify_plan
)


# ==========================================
# DATA PREPARATION
# ==========================================

def prepare_data(data):

    data = data.copy()

    if "scenario_id" in data.columns:
        data["scenario_id"] = (
            data["scenario_id"]
            .astype(str)
            .str.strip()
        )

    if "event_time" in data.columns:
        data["event_time"] = pd.to_datetime(
            data["event_time"],
            errors="coerce"
        )

    if "arrival_time" in data.columns:
        data["arrival_time"] = pd.to_datetime(
            data["arrival_time"],
            errors="coerce"
        )

    if "trust_score" in data.columns:
        data["trust_score"] = pd.to_numeric(
            data["trust_score"],
            errors="coerce"
        ).fillna(0.5)

    if "value" in data.columns:
        data["numeric_value"] = pd.to_numeric(
            data["value"],
            errors="coerce"
        )

    if "signature_valid" in data.columns:
        data["signature_valid"] = (
            data["signature_valid"]
            .astype(str)
            .str.strip()
            .str.lower()
            .isin(["true", "1", "yes"])
        )

    text_columns = [
        column for column in [
            "event_type",
            "source",
            "component_id",
            "note",
            "value"
        ]
        if column in data.columns
    ]

    data["search_text"] = (
        data[text_columns]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
        .str.lower()
    )

    return data


# ==========================================
# LOAD ALL VISIBLE DATASETS
# ==========================================

def load_all_data():

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Main dataset not found: {DATA_PATH}"
        )

    original_data = load_events(DATA_PATH)

    if not PARADOX_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Paradox dataset not found: {PARADOX_DATA_PATH}"
        )

    paradox_data = load_events(PARADOX_DATA_PATH)

    full_data = pd.concat(
        [original_data, paradox_data],
        ignore_index=True
    )

    full_data = prepare_data(full_data)

    return full_data


# ==========================================
# RUN COMPLETE PIPELINE
# ==========================================

def run_pipeline(selected_scenario):

    selected_scenario = str(
        selected_scenario
    ).strip().upper()

    print("\n==========================================")
    print("       CHRONOS-X CENTRAL PIPELINE")
    print("==========================================")

    print("\nLoading all datasets...")

    full_data = load_all_data()

    available_scenarios = set(
        full_data["scenario_id"].dropna().unique()
    )

    if selected_scenario not in available_scenarios:

        raise ValueError(
            f"Unknown scenario: {selected_scenario}. "
            f"Available scenarios: "
            f"{sorted(available_scenarios)}"
        )

    scenario_data = full_data[
        full_data["scenario_id"] == selected_scenario
    ].copy()

    if scenario_data.empty:
        raise ValueError(
            f"No events found for {selected_scenario}"
        )

    print("Dataset loaded successfully.")
    print("Selected scenario:", selected_scenario)
    print("Events:", len(scenario_data))

    # ======================================
    # M1: TEMPORAL RECONSTRUCTION
    # ======================================

    print("\n[M1] Temporal Reconstruction")

    event_history, arrival_history, duplicates = (
        reconstruct_scenario(
            scenario_data.copy()
        )
    )

    print("M1 completed.")

    # ======================================
    # M2: CAUSAL INVESTIGATION
    # ======================================

    print("\n[M2] Causal Investigation")

    hypotheses, causal_graph = investigate_scenario(
        scenario_data.copy()
    )

    root_cause = (
        hypotheses[0]["cause"]
        if hypotheses
        else "INSUFFICIENT EVIDENCE"
    )

    print("M2 completed.")

    # ======================================
    # M3: COUNTERFACTUAL SIMULATION
    # ======================================

    print("\n[M3] Counterfactual Future Simulation")

    m3_result = run_scenario_simulation(
        scenario_data.copy(),
        selected_scenario
    )

    simulation_results = m3_result["results"]

    print("M3 completed.")
    print(
        "Simulation candidates:",
        len(simulation_results)
    )

    # ======================================
    # M4: MULTI-AGENT ORCHESTRATION
    # ======================================

    print("\n[M4] Multi-Agent Orchestration")

    orchestrator = MultiAgentOrchestrator()

    agent_results = orchestrator.run(
        scenario_id=selected_scenario,
        root_cause=root_cause,
        simulation_results=simulation_results
    )

    print("M4 completed.")

    # ======================================
    # M5: RISK-AWARE OPTIMIZATION
    # ======================================

    print("\n[M5] Risk-Aware Optimization")

    m5_result = optimize_scenario(
        scenario_data.copy(),
        selected_scenario
    )

    m5_plan = build_plan_from_m5(
        m5_result
    )

    print("M5 completed.")

    # ======================================
    # M6: ADVERSARIAL DETECTION
    # ======================================

    print("\n[M6] Adversarial Detection")

    m6_full_results = detect_attacks(
        full_data.copy()
    )

    m6_scenario_results = m6_full_results[
        m6_full_results["scenario_id"] == selected_scenario
    ].copy()

    flagged_events = m6_scenario_results[
        m6_scenario_results["detection_status"]
        == "REVIEW_REQUIRED"
    ]

    print("M6 completed.")
    print(
        "Events requiring review:",
        len(flagged_events)
    )

    # ======================================
    # M7: SAFETY VERIFICATION
    # ======================================

    print("\n[M7] Safety Verification")

    safety_result = verify_plan(
        selected_scenario,
        m5_plan,
        m6_full_results
    )

    print("M7 completed.")

    # ======================================
    # FINAL PIPELINE RESULT
    # ======================================

    result = {

        "scenario_id": selected_scenario,

        "m1": {
            "event_history": event_history,
            "arrival_history": arrival_history,
            "duplicates": duplicates
        },

        "m2": {
            "hypotheses": hypotheses,
            "root_cause": root_cause,
            "graph_nodes": causal_graph.number_of_nodes(),
            "graph_edges": causal_graph.number_of_edges()
        },

        "m3": m3_result,

        "m4": agent_results,

        "m5": m5_result,

        "m6": m6_scenario_results,

        "m7": safety_result
    }

    print("\n==========================================")
    print("       PIPELINE EXECUTION COMPLETED")
    print("==========================================")

    return result


# ==========================================
# PRINT FINAL REPORT
# ==========================================

def print_pipeline_report(result):

    print("\n==========================================")
    print("       CHRONOS-X FINAL REPORT")
    print("==========================================")

    print("\nSCENARIO:", result["scenario_id"])

    # M1
    print("\nM1 - TEMPORAL RECONSTRUCTION")

    print(
        "Event history:",
        len(result["m1"]["event_history"])
    )

    print(
        "Arrival history:",
        len(result["m1"]["arrival_history"])
    )

    print(
        "Duplicates:",
        result["m1"]["duplicates"]
    )

    # M2
    print("\nM2 - CAUSAL INVESTIGATION")

    print(
        "Root cause hypothesis:",
        result["m2"]["root_cause"]
    )

    print(
        "Hypotheses:",
        len(result["m2"]["hypotheses"])
    )

    print(
        "Graph nodes:",
        result["m2"]["graph_nodes"]
    )

    print(
        "Graph edges:",
        result["m2"]["graph_edges"]
    )

    # M3
    print("\nM3 - COUNTERFACTUAL SIMULATION")

    print(
        "Events analysed:",
        result["m3"]["events_analysed"]
    )

    print(
        "Best simulated option:",
        result["m3"]["best_simulated_option"]
    )

    for simulation in result["m3"]["results"]:

        print(
            simulation["action"],
            "| Objective:",
            round(simulation["objective_score"], 2),
            "| 95th percentile:",
            round(simulation["percentile_95"], 2)
        )

    # M4
    print("\nM4 - MULTI-AGENT SYSTEM")

    print(
        "Agent result:",
        result["m4"]
    )

    # M5
    print("\nM5 - RISK-AWARE OPTIMIZATION")

    print(
        "Optimized plan:",
        result["m5"]["optimized"]["plan"]
    )

    print(
        "Feasible:",
        result["m5"]["feasible"]
    )

    # M6
    print("\nM6 - ADVERSARIAL DETECTION")

    print(
        "Records analysed:",
        len(result["m6"])
    )

    if "detection_status" in result["m6"].columns:

        print(
            "Flagged records:",
            (
                result["m6"]["detection_status"]
                == "REVIEW_REQUIRED"
            ).sum()
        )

        print(
            "High-priority records:",
            (
                result["m6"]["review_priority"]
                == "HIGH"
            ).sum()
        )

    # M7
    print("\nM7 - SAFETY VERIFICATION")

    print(
        "Proposed actions:",
        result["m7"]["actions"]
    )

    print(
        "Resources:",
        result["m7"]["resources"]
    )

    print(
        "Time:",
        result["m7"]["time"]
    )

    print(
        "High-priority events:",
        result["m7"]["high_priority_events"]
    )

    print(
        "Safety status:",
        result["m7"]["status"]
    )

    for reason in result["m7"]["reasons"]:
        print("-", reason)

    print("\n==========================================")
    print("CHRONOS-X EXECUTION FINISHED")
    print("==========================================")

    print(
        "\nNOTE: All data and intervention effects are "
        "synthetic and illustrative. Results are not "
        "real-world industrial operating instructions."
    )


# ==========================================
# MANUAL TEST
# ==========================================

if __name__ == "__main__":

    result = run_pipeline("CX-006")

    print_pipeline_report(result)
