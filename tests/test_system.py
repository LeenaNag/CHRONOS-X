
import pytest

from backend.pipeline import run_pipeline


@pytest.mark.parametrize(
    "scenario_id",
    [
        "CX-001",
        "CX-002",
        "CX-003",
        "CX-004",
        "CX-005",
    ],
)
def test_pipeline_runs_for_all_scenarios(scenario_id):
    result = run_pipeline(scenario_id)

    assert result["scenario_id"] == scenario_id

    # M1: Temporal reconstruction
    assert len(result["m1"]["event_history"]) > 0
    assert len(result["m1"]["arrival_history"]) > 0

    # M2: Causal investigation
    assert isinstance(result["m2"]["hypotheses"], list)
    assert result["m2"]["root_cause"]

    # M3: Counterfactual simulation
    assert len(result["m3"]["results"]) > 0

    # M4: Multi-agent system
    assert result["m4"]["investigation"]["status"] == "INVESTIGATION_COMPLETED"
    assert result["m4"]["prediction"]["status"] == "PREDICTION_COMPLETED"
    assert result["m4"]["optimization"]["status"] == "OPTION_IDENTIFIED"
    assert result["m4"]["safety"]["decision"] == "REQUIRES_VALIDATION"
    assert "red_team" in result["m4"]

    # M5: Risk-aware optimization
    assert "optimized" in result["m5"]
    assert "feasible" in result["m5"]

    # M6: Adversarial detection
    assert result["m6"] is not None

    # M7: Safety verification
    assert result["m7"]["status"] in ["PASS", "FAIL", "UNKNOWN"]


def test_dataset_contains_five_scenarios():
    from modules.temporal.reconstruction import load_events

    data = load_events("data/chronos_x_events.csv")

    assert data["scenario_id"].nunique() == 5
    assert len(data) > 0
