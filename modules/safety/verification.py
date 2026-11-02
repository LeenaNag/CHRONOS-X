
import pandas as pd
from pathlib import Path

from modules.optimization.risk_optimizer import (
    load_data as load_m5_data,
    optimize_scenario
)


# =====================================================
# CHRONOS-X M7: SAFETY VERIFICATION
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

M6_PATH = PROJECT_ROOT / "data" / "m6_detection_results.csv"

OUTPUT_PATH = PROJECT_ROOT / "data" / "m7_safety_results.csv"

RESOURCE_BUDGET = 10
TIME_DEADLINE = 20


# =====================================================
# ALLOWED ACTIONS
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
        "REDUCE_MACHINE_LOAD",
        "BACKUP_COOLING",
        "INSPECT_MECHANICAL"
    ],

    "CX-003": [
        "ISOLATE_NETWORK",
        "REDUCE_MACHINE_LOAD",
        "VERIFY_EVIDENCE"
    ],

    "CX-004": [
        "VERIFY_EVIDENCE",
        "REDUCE_MACHINE_LOAD",
        "BACKUP_COOLING",
        "INSPECT_MECHANICAL"
    ],

    "CX-005": [
        "INSPECT_MECHANICAL",
        "REDUCE_MACHINE_LOAD",
        "VERIFY_EVIDENCE",
        "BACKUP_COOLING"
    ],

    # CX-006 Paradox Protocol
    # RECOVERY_ACTION_A is intentionally excluded
    # because its recommendation is untrusted.

    "CX-006": [
        "VERIFY_EVIDENCE",
        "BACKUP_COOLING",
        "REDUCE_MACHINE_LOAD",
        "ISOLATE_NETWORK"
    ]
}


# =====================================================
# LOAD M6 DETECTION RESULTS
# =====================================================

def load_m6_results():

    if not M6_PATH.exists():

        raise FileNotFoundError(
            f"M6 results not found: {M6_PATH}. "
            "Run M6 attack detection first."
        )

    data = pd.read_csv(M6_PATH)

    required_columns = [
        "scenario_id",
        "review_priority"
    ]

    missing = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing:

        raise ValueError(
            f"M6 results are missing columns: {missing}"
        )

    data["scenario_id"] = (
        data["scenario_id"]
        .astype(str)
        .str.strip()
    )

    data["review_priority"] = (
        data["review_priority"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return data


# =====================================================
# BUILD PLAN FROM M5
# =====================================================

def build_plan_from_m5(m5_result):
    """
    Extract the optimized action plan from M5.
    """

    optimized_result = m5_result["optimized"]

    actions = optimized_result["plan"]

    if actions == ["NO_ACTION"]:
        actions = []

    return {

        "actions": actions,

        "resources": m5_result["resources_used"],

        "time": m5_result["time_required"],

        "feasible": m5_result["feasible"],

        "feasibility_reason": (
            m5_result["feasibility_reason"]
        )
    }


# =====================================================
# VERIFY OPTIMIZED PLAN
# =====================================================

def verify_plan(scenario_id, plan, m6_data):

    scenario_id = str(scenario_id).strip()

    reasons = []

    actions = plan["actions"]

    resources = plan["resources"]

    time_required = plan["time"]

    # -------------------------------------------------
    # CHECK 1: ACTION VALIDITY
    # -------------------------------------------------

    allowed = ALLOWED_ACTIONS.get(
        scenario_id,
        []
    )

    invalid_actions = [
        action for action in actions
        if action not in allowed
    ]

    if invalid_actions:

        reasons.append(
            f"Actions not allowed: {invalid_actions}"
        )

    # -------------------------------------------------
    # CHECK 2: RESOURCE BUDGET
    # -------------------------------------------------

    if resources > RESOURCE_BUDGET:

        reasons.append(
            "Resource budget exceeded"
        )

    if resources < 0:

        reasons.append(
            "Invalid negative resource usage"
        )

    # -------------------------------------------------
    # CHECK 3: VIRTUAL DEADLINE
    # -------------------------------------------------

    if time_required > TIME_DEADLINE:

        reasons.append(
            "Virtual deadline exceeded"
        )

    if time_required < 0:

        reasons.append(
            "Invalid negative execution time"
        )

    # -------------------------------------------------
    # CHECK 4: M5 FEASIBILITY
    # -------------------------------------------------

    if not plan.get("feasible", False):

        reasons.append(
            "M5 optimizer marked this plan as infeasible"
        )

    # -------------------------------------------------
    # CHECK 5: M6 ADVERSARIAL DETECTION
    # -------------------------------------------------

    scenario_events = m6_data[
        m6_data["scenario_id"] == scenario_id
    ].copy()

    high_priority = scenario_events[
        scenario_events["review_priority"] == "HIGH"
    ]

    high_priority_count = len(high_priority)

    suspicious_event_ids = []

    if (
        high_priority_count > 0
        and "event_id" in high_priority.columns
    ):

        suspicious_event_ids = (
            high_priority["event_id"]
            .dropna()
            .astype(str)
            .tolist()
        )

    # -------------------------------------------------
    # CHECK 6: M6 EVIDENCE AVAILABILITY
    # -------------------------------------------------

    if scenario_events.empty:

        reasons.append(
            "No M6 detection records found for this scenario"
        )

    # -------------------------------------------------
    # FINAL SAFETY STATUS
    # -------------------------------------------------

    if reasons:

        status = "FAIL"

    elif high_priority_count > 0:

        status = "UNKNOWN"

        reasons.append(
            f"{high_priority_count} high-priority events "
            "require independent evidence verification"
        )

        if suspicious_event_ids:

            reasons.append(
                "Events requiring review: "
                + ", ".join(suspicious_event_ids)
            )

    else:

        status = "PASS"

        reasons.append(
            "All implemented prototype safety checks passed"
        )

    return {

        "scenario_id": scenario_id,

        "actions": actions,

        "resources": resources,

        "time": time_required,

        "status": status,

        "high_priority_events": high_priority_count,

        "reasons": reasons
    }


# =====================================================
# MAIN M7 EXECUTION
# =====================================================

def main():

    print("\n========== CHRONOS-X M7 ==========")

    print("Starting safety verification...")

    # Load M6 detection results.
    m6_data = load_m6_results()

    print(
        "M6 detection records loaded:",
        len(m6_data)
    )

    # Load all scenarios using M5 loader.
    m5_data = load_m5_data()

    print(
        "Scenarios available:",
        sorted(m5_data["scenario_id"].unique())
    )

    reports = []

    # -------------------------------------------------
    # VERIFY EACH SCENARIO
    # -------------------------------------------------

    for scenario_id, scenario in m5_data.groupby(
        "scenario_id"
    ):

        print(
            f"\nProcessing scenario: {scenario_id}"
        )

        # Obtain M5 optimized plan.
        m5_result = optimize_scenario(
            scenario,
            scenario_id
        )

        # Convert M5 result into safety plan.
        plan = build_plan_from_m5(m5_result)

        # Verify the proposed plan.
        result = verify_plan(
            scenario_id,
            plan,
            m6_data
        )

        reports.append(result)

        print("\nScenario:", result["scenario_id"])

        print(
            "Proposed actions:",
            result["actions"]
        )

        print(
            f"Resource usage: {result['resources']}/"
            f"{RESOURCE_BUDGET}"
        )

        print(
            f"Time required: {result['time']}/"
            f"{TIME_DEADLINE}"
        )

        print(
            "High-priority events:",
            result["high_priority_events"]
        )

        print(
            "Safety status:",
            result["status"]
        )

        for reason in result["reasons"]:

            print("-", reason)

    # -------------------------------------------------
    # SAVE RESULTS
    # -------------------------------------------------

    output = pd.DataFrame(reports)

    output["actions"] = output["actions"].apply(
        lambda values: " + ".join(values)
    )

    output["reasons"] = output["reasons"].apply(
        lambda values: " | ".join(values)
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # -------------------------------------------------
    # SUMMARY
    # -------------------------------------------------

    print("\n========== M7 SUMMARY ==========")

    print(
        output["status"]
        .value_counts()
        .to_string()
    )

    print(
        "\nDetailed results saved to:",
        OUTPUT_PATH
    )

    print("\nM7 SAFETY VERIFICATION COMPLETED.")

    print(
        "\nNOTE: PASS represents only implemented "
        "prototype checks. UNKNOWN requires further "
        "verification. This is not real-world "
        "industrial safety certification."
    )


if __name__ == "__main__":
    main()
