
import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================
# CHRONOS-X M3: FUTURE SIMULATION
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = PROJECT_ROOT / "data" / "chronos_x_events.csv"
PARADOX_DATA_PATH = (
    PROJECT_ROOT / "data" / "paradox_protocol" / "cx006_events.csv"
)

NUMBER_OF_ROLLOUTS = 200
SIMULATION_STEPS = 10
RANDOM_SEED = 42


# ==========================================
# LOAD AND PREPARE DATA
# ==========================================

def load_data(include_paradox=True):

    data = pd.read_csv(DATA_PATH)

    if include_paradox and PARADOX_DATA_PATH.exists():
        paradox_data = pd.read_csv(PARADOX_DATA_PATH)
        data = pd.concat(
            [data, paradox_data],
            ignore_index=True
        )

    required_columns = [
        "scenario_id", "event_time", "event_type",
        "value", "trust_score", "signature_valid"
    ]

    missing = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing:
        raise ValueError(f"Missing dataset columns: {missing}")

    data["event_time"] = pd.to_datetime(
        data["event_time"], errors="coerce"
    )

    data["numeric_value"] = pd.to_numeric(
        data["value"], errors="coerce"
    )

    text_columns = [
        col for col in [
            "event_type", "source", "component_id", "note", "value"
        ] if col in data.columns
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
# TREND CALCULATION
# ==========================================

def calculate_trend(scenario, keywords):

    pattern = "|".join(keywords)

    matched = scenario[
        scenario["search_text"].str.contains(
            pattern, regex=True, na=False
        )
    ].copy()

    matched = matched.dropna(
        subset=["numeric_value", "event_time"]
    )

    matched = matched.sort_values("event_time")

    if len(matched) < 4:
        return 0.0

    values = matched["numeric_value"]
    quarter = max(1, len(values) // 4)

    first_median = values.iloc[:quarter].median()
    last_median = values.iloc[-quarter:].median()

    if abs(first_median) < 0.000001:
        return 0.0

    return (
        (last_median - first_median) /
        abs(first_median)
    ) * 100


# ==========================================
# SCENARIO ANALYSIS
# ==========================================

def analyse_scenario(scenario):

    temperature_rise = max(
        0,
        calculate_trend(scenario, ["temperature", "temp"])
    )

    coolant_change = calculate_trend(
        scenario, ["coolant", "cooling.flow"]
    )

    coolant_drop = max(0, -coolant_change)

    vibration_rise = max(
        0,
        calculate_trend(scenario, ["vibration", "vib"])
    )

    pressure_rise = max(
        0,
        calculate_trend(scenario, ["pressure"])
    )

    network_alerts = scenario[
        scenario["search_text"].str.contains(
            "network.alert|intrusion|network",
            regex=True,
            na=False
        )
    ].shape[0]

    low_trust = (
        pd.to_numeric(
            scenario["trust_score"], errors="coerce"
        ) < 0.6
    ).mean()

    invalid_signatures = (
        scenario["signature_valid"]
        .astype(str)
        .str.lower()
        .isin(["false", "0", "no"])
        .mean()
    )

    maintenance_conflict = (
        scenario["search_text"].str.contains(
            "maintenance", na=False
        )
        &
        scenario["search_text"].str.contains(
            "healthy", na=False
        )
    ).any()

    # Illustrative risk index, not a real-world probability.
    initial_risk = 20

    initial_risk += min(temperature_rise * 0.6, 20)
    initial_risk += min(coolant_drop * 0.35, 20)
    initial_risk += min(vibration_rise * 0.2, 20)
    initial_risk += min(pressure_rise * 0.15, 10)
    initial_risk += min(network_alerts * 2, 12)
    initial_risk += low_trust * 10
    initial_risk += invalid_signatures * 8

    if maintenance_conflict:
        initial_risk += 8

    initial_risk = float(
        np.clip(initial_risk, 0, 100)
    )

    return {
        "initial_risk": initial_risk,
        "temperature_rise": temperature_rise,
        "coolant_drop": coolant_drop,
        "vibration_rise": vibration_rise,
        "pressure_rise": pressure_rise,
        "network_alerts": network_alerts,
        "low_trust": low_trust,
        "invalid_signatures": invalid_signatures
    }


# ==========================================
# SIMULATION ACTIONS
# ==========================================

ACTIONS = [
    "NO_ACTION",
    "BACKUP_COOLING",
    "REDUCE_MACHINE_LOAD",
    "ISOLATE_NETWORK",
    "VERIFY_EVIDENCE",
    "INSPECT_MECHANICAL"
]


ACTION_EFFECTS = {

    "CX-001": {
        "NO_ACTION": (0, 1.00),
        "BACKUP_COOLING": (18, 0.55),
        "REDUCE_MACHINE_LOAD": (12, 0.70),
        "ISOLATE_NETWORK": (2, 0.95),
        "VERIFY_EVIDENCE": (2, 0.95),
        "INSPECT_MECHANICAL": (3, 0.90)
    },

    "CX-002": {
        "NO_ACTION": (0, 1.00),
        "BACKUP_COOLING": (2, 0.95),
        "REDUCE_MACHINE_LOAD": (3, 0.90),
        "ISOLATE_NETWORK": (6, 0.85),
        "VERIFY_EVIDENCE": (16, 0.70),
        "INSPECT_MECHANICAL": (2, 0.95)
    },

    "CX-003": {
        "NO_ACTION": (0, 1.00),
        "BACKUP_COOLING": (2, 0.95),
        "REDUCE_MACHINE_LOAD": (5, 0.85),
        "ISOLATE_NETWORK": (22, 0.55),
        "VERIFY_EVIDENCE": (3, 0.90),
        "INSPECT_MECHANICAL": (2, 0.95)
    },

    "CX-004": {
        "NO_ACTION": (0, 1.00),
        "BACKUP_COOLING": (10, 0.70),
        "REDUCE_MACHINE_LOAD": (8, 0.80),
        "ISOLATE_NETWORK": (2, 0.95),
        "VERIFY_EVIDENCE": (14, 0.75),
        "INSPECT_MECHANICAL": (3, 0.90)
    },

    "CX-005": {
        "NO_ACTION": (0, 1.00),
        "BACKUP_COOLING": (2, 0.95),
        "REDUCE_MACHINE_LOAD": (12, 0.70),
        "ISOLATE_NETWORK": (1, 0.98),
        "VERIFY_EVIDENCE": (3, 0.90),
        "INSPECT_MECHANICAL": (20, 0.55)
    },

    # CX-006 uses illustrative simulation assumptions.
    # RECOVERY_ACTION_A is untrusted and is evaluated only
    # as a counterfactual candidate, never as an approved action.
    "CX-006": {
        "NO_ACTION": (0, 1.00),
        "BACKUP_COOLING": (15, 0.65),
        "REDUCE_MACHINE_LOAD": (12, 0.70),
        "ISOLATE_NETWORK": (8, 0.80),
        "VERIFY_EVIDENCE": (10, 0.75),
        "INSPECT_MECHANICAL": (4, 0.90),
        "RECOVERY_ACTION_A": (22, 0.50)
    }
}


ACTION_COSTS = {
    "NO_ACTION": 0,
    "BACKUP_COOLING": 8,
    "REDUCE_MACHINE_LOAD": 5,
    "ISOLATE_NETWORK": 10,
    "VERIFY_EVIDENCE": 3,
    "INSPECT_MECHANICAL": 6,
    "RECOVERY_ACTION_A": 0
}


# Delayed effects are abstract simulation penalties.
# They do not describe real equipment behaviour.
DELAYED_EFFECTS = {
    "CX-006": {
        "RECOVERY_ACTION_A": {
            "delay_step": 4,
            "risk_penalty": 18
        }
    }
}


# ==========================================
# MONTE CARLO SIMULATION
# ==========================================

def simulate_action(
    initial_risk,
    action,
    scenario_id,
    seed=RANDOM_SEED
):

    if scenario_id not in ACTION_EFFECTS:
        raise ValueError(
            f"Unknown scenario: {scenario_id}"
        )

    if action not in ACTION_EFFECTS[scenario_id]:
        raise ValueError(
            f"Unsupported action {action} for {scenario_id}"
        )

    risk_reduction, drift_multiplier = (
        ACTION_EFFECTS[scenario_id][action]
    )

    delayed_effect = (
        DELAYED_EFFECTS
        .get(scenario_id, {})
        .get(action)
    )

    rng = np.random.default_rng(seed)

    peak_risks = []
    final_risks = []

    drift = 0.25 + (initial_risk * 0.012)

    for rollout in range(NUMBER_OF_ROLLOUTS):

        risk = max(
            0,
            initial_risk - risk_reduction
        )

        risk_history = [risk]

        for step in range(SIMULATION_STEPS):

            noise = rng.normal(0, 2.0)

            risk += (
                drift * drift_multiplier
                + noise
            )

            # Apply the delayed secondary effect.
            if (
                delayed_effect is not None
                and step + 1 == delayed_effect["delay_step"]
            ):
                risk += delayed_effect["risk_penalty"]

            risk = float(
                np.clip(risk, 0, 100)
            )

            risk_history.append(risk)

        peak_risks.append(max(risk_history))
        final_risks.append(risk_history[-1])

    average_peak = float(np.mean(peak_risks))
    average_final = float(np.mean(final_risks))

    percentile_95 = float(
        np.percentile(peak_risks, 95)
    )

    high_risk_frequency = float(
        (np.array(peak_risks) >= 80).mean() * 100
    )

    objective_score = (
        average_peak
        + ACTION_COSTS[action] * 0.4
    )

    return {
        "action": action,
        "average_peak": average_peak,
        "average_final": average_final,
        "percentile_95": percentile_95,
        "high_risk_frequency": high_risk_frequency,
        "objective_score": objective_score,
        "delayed_effect_modelled": delayed_effect is not None
    }


# ==========================================
# RUN ONE SCENARIO
# ==========================================

def run_scenario_simulation(
    data,
    scenario_id,
    seed=RANDOM_SEED
):

    scenario = data[
        data["scenario_id"] == scenario_id
    ].copy()

    if scenario.empty:
        raise ValueError(
            f"No data found for scenario {scenario_id}"
        )

    features = analyse_scenario(scenario)

    scenario_actions = list(
        ACTION_EFFECTS[scenario_id].keys()
    )

    results = []

    for action_index, action in enumerate(scenario_actions):

        result = simulate_action(
            features["initial_risk"],
            action,
            scenario_id,
            seed + action_index
        )

        results.append(result)

    results.sort(
        key=lambda item: item["objective_score"]
    )

    return {
        "scenario_id": scenario_id,
        "events_analysed": len(scenario),
        "features": features,
        "results": results,
        "best_simulated_option": results[0]["action"],
        "status": "SIMULATION_REQUIRES_SAFETY_VALIDATION"
    }


# ==========================================
# MAIN EXECUTION
# ==========================================

def main():

    data = load_data()

    print("\n========== CHRONOS-X M3 ==========")

    scenario_ids = sorted(
        data["scenario_id"].dropna().unique()
    )

    for scenario_index, scenario_id in enumerate(scenario_ids):

        output = run_scenario_simulation(
            data,
            scenario_id,
            RANDOM_SEED + scenario_index * 100
        )

        features = output["features"]

        print("\n--------------------------------------")
        print("SCENARIO:", scenario_id)
        print(
            "Events analysed:",
            output["events_analysed"]
        )

        print(
            "Initial simulated risk index:",
            round(features["initial_risk"], 2),
            "/ 100"
        )

        print("\nObserved trend indicators:")

        for key in [
            "temperature_rise",
            "coolant_drop",
            "vibration_rise",
            "pressure_rise"
        ]:
            print(
                key,
                ":",
                round(features[key], 2),
                "%"
            )

        print(
            "Network-related records:",
            features["network_alerts"]
        )

        print("\nCOUNTERFACTUAL ACTION COMPARISON:")

        for result in output["results"]:

            print(
                result["action"],
                "| Average peak:",
                round(result["average_peak"], 2),
                "| 95th percentile:",
                round(result["percentile_95"], 2),
                "| High risk %:",
                round(result["high_risk_frequency"], 2),
                "| Delayed effect:",
                result["delayed_effect_modelled"]
            )

        print(
            "\nBEST SIMULATED OPTION:",
            output["best_simulated_option"]
        )

        print(
            "Status:",
            output["status"]
        )

    print("\nM3 COUNTERFACTUAL SIMULATION COMPLETED")

    print(
        "All values use illustrative assumptions, "
        "not real-world probabilities."
    )


if __name__ == "__main__":
    main()
