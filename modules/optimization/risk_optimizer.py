
import itertools
import math
from pathlib import Path

import numpy as np
import pandas as pd


# =====================================================
# CHRONOS-X M5: RISK-AWARE OPTIMIZATION
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = PROJECT_ROOT / "data" / "chronos_x_events.csv"

PARADOX_DATA_PATH = (
    PROJECT_ROOT / "data" / "paradox_protocol" / "cx006_events.csv"
)

NUMBER_OF_ROLLOUTS = 200
SIMULATION_STEPS = 10

RESOURCE_BUDGET = 10
TIME_DEADLINE = 20

RISK_WEIGHT = 1.0
CVAR_WEIGHT = 0.35
COST_WEIGHT = 0.5

RANDOM_SEED = 42


# =====================================================
# LOAD DATA: CX-001 TO CX-006
# =====================================================

def load_data():

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Main dataset not found: {DATA_PATH}"
        )

    data = pd.read_csv(DATA_PATH)

    if not PARADOX_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Paradox dataset not found: {PARADOX_DATA_PATH}"
        )

    paradox_data = pd.read_csv(PARADOX_DATA_PATH)

    data = pd.concat(
        [data, paradox_data],
        ignore_index=True
    )

    required_columns = [
        "scenario_id",
        "event_time",
        "event_type",
        "value",
        "trust_score"
    ]

    missing = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    data["scenario_id"] = (
        data["scenario_id"]
        .astype(str)
        .str.strip()
    )

    data["event_time"] = pd.to_datetime(
        data["event_time"],
        errors="coerce"
    )

    data["numeric_value"] = pd.to_numeric(
        data["value"],
        errors="coerce"
    )

    data["trust_score"] = pd.to_numeric(
        data["trust_score"],
        errors="coerce"
    ).fillna(0.5)

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

    print("Main dataset loaded.")
    print("CX-006 Paradox dataset loaded.")

    return data


# =====================================================
# ACTION DEFINITIONS
# =====================================================

ACTIONS = {

    "BACKUP_COOLING": {
        "resources": 5,
        "time": 8,
        "cost": 8
    },

    "REDUCE_MACHINE_LOAD": {
        "resources": 3,
        "time": 5,
        "cost": 5
    },

    "ISOLATE_NETWORK": {
        "resources": 6,
        "time": 7,
        "cost": 10
    },

    "VERIFY_EVIDENCE": {
        "resources": 1,
        "time": 3,
        "cost": 3
    },

    "INSPECT_MECHANICAL": {
        "resources": 4,
        "time": 8,
        "cost": 6
    }
}


# =====================================================
# ALLOWED ACTIONS FOR EACH SCENARIO
# =====================================================

ALLOWED_ACTIONS = {

    "CX-001": [
        "BACKUP_COOLING",
        "REDUCE_MACHINE_LOAD",
        "VERIFY_EVIDENCE",
        "INSPECT_MECHANICAL"
    ],

    "CX-002": [
        "VERIFY_EVIDENCE",
        "ISOLATE_NETWORK",
        "REDUCE_MACHINE_LOAD"
    ],

    "CX-003": [
        "ISOLATE_NETWORK",
        "VERIFY_EVIDENCE",
        "REDUCE_MACHINE_LOAD"
    ],

    "CX-004": [
        "VERIFY_EVIDENCE",
        "BACKUP_COOLING",
        "REDUCE_MACHINE_LOAD"
    ],

    "CX-005": [
        "INSPECT_MECHANICAL",
        "REDUCE_MACHINE_LOAD",
        "VERIFY_EVIDENCE"
    ],

    "CX-006": [
        "VERIFY_EVIDENCE",
        "BACKUP_COOLING",
        "REDUCE_MACHINE_LOAD",
        "ISOLATE_NETWORK"
    ]
}


# =====================================================
# ILLUSTRATIVE RISK REDUCTION ASSUMPTIONS
# =====================================================

RISK_REDUCTION = {

    "CX-001": {
        "BACKUP_COOLING": 18,
        "REDUCE_MACHINE_LOAD": 12,
        "VERIFY_EVIDENCE": 2,
        "INSPECT_MECHANICAL": 3
    },

    "CX-002": {
        "VERIFY_EVIDENCE": 16,
        "ISOLATE_NETWORK": 6,
        "REDUCE_MACHINE_LOAD": 3
    },

    "CX-003": {
        "ISOLATE_NETWORK": 22,
        "VERIFY_EVIDENCE": 3,
        "REDUCE_MACHINE_LOAD": 5
    },

    "CX-004": {
        "VERIFY_EVIDENCE": 14,
        "BACKUP_COOLING": 10,
        "REDUCE_MACHINE_LOAD": 8
    },

    "CX-005": {
        "INSPECT_MECHANICAL": 20,
        "REDUCE_MACHINE_LOAD": 12,
        "VERIFY_EVIDENCE": 3
    },

    "CX-006": {
        "VERIFY_EVIDENCE": 10,
        "BACKUP_COOLING": 15,
        "REDUCE_MACHINE_LOAD": 12,
        "ISOLATE_NETWORK": 8
    }
}


# =====================================================
# TREND CALCULATION
# =====================================================

def calculate_trend(scenario, keywords):

    matched = scenario[
        scenario["search_text"].str.contains(
            "|".join(keywords),
            regex=True,
            na=False
        )
    ].dropna(
        subset=["numeric_value", "event_time"]
    )

    matched = matched.sort_values("event_time")

    if len(matched) < 4:
        return 0.0

    values = matched["numeric_value"]

    quarter = max(1, len(values) // 4)

    first = values.iloc[:quarter].median()
    last = values.iloc[-quarter:].median()

    if abs(first) < 0.000001:
        return 0.0

    return (
        (last - first) / abs(first)
    ) * 100


# =====================================================
# INITIAL RISK CALCULATION
# =====================================================

def calculate_initial_risk(scenario):

    temp_rise = max(
        0,
        calculate_trend(
            scenario,
            ["temperature", "temp"]
        )
    )

    coolant_drop = max(
        0,
        -calculate_trend(
            scenario,
            ["coolant", "cooling.flow"]
        )
    )

    vibration_rise = max(
        0,
        calculate_trend(
            scenario,
            ["vibration", "vib"]
        )
    )

    pressure_rise = max(
        0,
        calculate_trend(
            scenario,
            ["pressure"]
        )
    )

    network_alerts = scenario[
        scenario["search_text"].str.contains(
            "network.alert|intrusion|network",
            regex=True,
            na=False
        )
    ].shape[0]

    low_trust = (
        scenario["trust_score"] < 0.6
    ).mean()

    invalid_signatures = 0

    if "signature_valid" in scenario.columns:

        invalid_signatures = (
            scenario["signature_valid"]
            .astype(str)
            .str.lower()
            .isin(["false", "0", "no"])
        ).mean()

    risk = 20

    risk += min(temp_rise * 0.6, 20)
    risk += min(coolant_drop * 0.35, 20)
    risk += min(vibration_rise * 0.2, 20)
    risk += min(pressure_rise * 0.15, 10)
    risk += min(network_alerts * 2, 12)
    risk += low_trust * 10
    risk += invalid_signatures * 8

    return float(np.clip(risk, 0, 100))


# =====================================================
# FEASIBILITY CHECK
# =====================================================

def check_feasibility(plan):

    for action in plan:

        if action not in ACTIONS:
            return False, f"UNKNOWN ACTION: {action}"

    resources = sum(
        ACTIONS[action]["resources"]
        for action in plan
    )

    duration = sum(
        ACTIONS[action]["time"]
        for action in plan
    )

    if resources > RESOURCE_BUDGET:
        return False, "RESOURCE LIMIT EXCEEDED"

    if duration > TIME_DEADLINE:
        return False, "TIME DEADLINE EXCEEDED"

    return True, "FEASIBLE UNDER PROTOTYPE RULES"


# =====================================================
# COUNTERFACTUAL PLAN SIMULATION
# =====================================================

def simulate_plan(
    initial_risk,
    plan,
    scenario_id,
    seed=RANDOM_SEED
):

    if scenario_id not in RISK_REDUCTION:
        raise ValueError(
            f"Unknown scenario: {scenario_id}"
        )

    for action in plan:

        if action not in RISK_REDUCTION[scenario_id]:
            raise ValueError(
                f"Action {action} is not defined for {scenario_id}"
            )

    feasible, reason = check_feasibility(plan)

    if not feasible:
        raise ValueError(reason)

    rng = np.random.default_rng(seed)

    total_cost = sum(
        ACTIONS[action]["cost"]
        for action in plan
    )

    risk = initial_risk

    for index, action in enumerate(plan):

        reduction = RISK_REDUCTION[scenario_id][action]

        risk -= reduction * (0.65 ** index)

    risk = float(np.clip(risk, 0, 100))

    peak_risks = []

    drift = 0.25 + (initial_risk * 0.012)

    for _ in range(NUMBER_OF_ROLLOUTS):

        current_risk = risk

        history = [current_risk]

        for _ in range(SIMULATION_STEPS):

            noise = rng.normal(0, 2.0)

            current_risk += drift + noise

            current_risk = float(
                np.clip(current_risk, 0, 100)
            )

            history.append(current_risk)

        peak_risks.append(max(history))

    average_peak = float(
        np.mean(peak_risks)
    )

    sorted_risks = np.sort(peak_risks)

    tail_count = max(
        1,
        math.ceil(NUMBER_OF_ROLLOUTS * 0.05)
    )

    cvar_95 = float(
        np.mean(sorted_risks[-tail_count:])
    )

    objective_score = (
        RISK_WEIGHT * average_peak
        + CVAR_WEIGHT * cvar_95
        + COST_WEIGHT * total_cost
    )

    return {

        "plan": list(plan) if plan else ["NO_ACTION"],

        "average_peak_risk": average_peak,

        "cvar_95": cvar_95,

        "cost": total_cost,

        "objective_score": objective_score
    }


# =====================================================
# GENERATE CANDIDATE PLANS
# =====================================================

def generate_plans(scenario_id):

    if scenario_id not in ALLOWED_ACTIONS:
        raise ValueError(
            f"Unknown scenario: {scenario_id}"
        )

    allowed = ALLOWED_ACTIONS[scenario_id]

    plans = [tuple()]

    for length in range(1, 3):

        for plan in itertools.permutations(
            allowed,
            length
        ):

            feasible, _ = check_feasibility(plan)

            if feasible:
                plans.append(plan)

    return plans


# =====================================================
# MAIN OPTIMIZATION FUNCTION
# =====================================================

def optimize_scenario(
    scenario,
    scenario_id,
    seed=RANDOM_SEED
):

    scenario_id = str(scenario_id).strip()

    if scenario.empty:
        raise ValueError(
            f"No data found for {scenario_id}"
        )

    if scenario_id not in ALLOWED_ACTIONS:
        raise ValueError(
            f"Unknown scenario: {scenario_id}"
        )

    initial_risk = calculate_initial_risk(scenario)

    plans = generate_plans(scenario_id)

    results = []

    for index, plan in enumerate(plans):

        result = simulate_plan(
            initial_risk,
            plan,
            scenario_id,
            seed + index
        )

        feasible, reason = check_feasibility(plan)

        result["feasible"] = feasible
        result["feasibility_reason"] = reason

        results.append(result)

    results.sort(
        key=lambda item: item["objective_score"]
    )

    no_action = next(
        result
        for result in results
        if result["plan"] == ["NO_ACTION"]
    )

    single_action_results = [
        result
        for result in results
        if len(result["plan"]) == 1
    ]

    greedy = min(
        single_action_results,
        key=lambda item: item["objective_score"]
    )

    optimized = results[0]

    actual_actions = (
        []
        if optimized["plan"] == ["NO_ACTION"]
        else optimized["plan"]
    )

    resources_used = sum(
        ACTIONS[action]["resources"]
        for action in actual_actions
    )

    time_required = sum(
        ACTIONS[action]["time"]
        for action in actual_actions
    )

    return {

        "scenario_id": scenario_id,

        "initial_risk": initial_risk,

        "no_action": no_action,

        "greedy": greedy,

        "optimized": optimized,

        "resources_used": resources_used,

        "resource_budget": RESOURCE_BUDGET,

        "time_required": time_required,

        "time_deadline": TIME_DEADLINE,

        "feasible": optimized["feasible"],

        "feasibility_reason": optimized["feasibility_reason"],

        "tested_plan_count": len(plans)
    }


# =====================================================
# RUN ALL SCENARIOS
# =====================================================

def main():

    data = load_data()

    print("\n========== CHRONOS-X M5 ==========")

    scenario_ids = sorted(
        data["scenario_id"].dropna().unique()
    )

    print("Scenarios loaded:", scenario_ids)

    for index, scenario_id in enumerate(scenario_ids):

        scenario = data[
            data["scenario_id"] == scenario_id
        ].copy()

        output = optimize_scenario(
            scenario,
            scenario_id,
            RANDOM_SEED + index * 1000
        )

        print("\n----------------------------------")
        print("SCENARIO:", scenario_id)
        print("Events analysed:", len(scenario))

        print(
            "Initial risk:",
            round(output["initial_risk"], 2)
        )

        for label in [
            "no_action",
            "greedy",
            "optimized"
        ]:

            result = output[label]

            print("\n", label.upper())
            print("Plan:", result["plan"])

            print(
                "Average peak risk:",
                round(result["average_peak_risk"], 2)
            )

            print(
                "CVaR 95:",
                round(result["cvar_95"], 2)
            )

            print("Cost:", result["cost"])

            print(
                "Objective score:",
                round(result["objective_score"], 2)
            )

        print(
            "\nResources:",
            output["resources_used"],
            "/",
            output["resource_budget"]
        )

        print(
            "Time:",
            output["time_required"],
            "/",
            output["time_deadline"]
        )

        print(
            "Feasibility:",
            output["feasibility_reason"]
        )

        print("M7 safety verification is required.")

    print("\nM5 OPTIMIZATION COMPLETED.")


if __name__ == "__main__":
    main()
