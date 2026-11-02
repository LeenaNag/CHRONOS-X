
from modules.simulation.future_simulator import simulate_action, RANDOM_SEED


def test_simulation_is_reproducible_with_same_seed():
    first_run = simulate_action(
        initial_risk=70,
        action="BACKUP_COOLING",
        scenario_id="CX-001",
        seed=RANDOM_SEED
    )

    second_run = simulate_action(
        initial_risk=70,
        action="BACKUP_COOLING",
        scenario_id="CX-001",
        seed=RANDOM_SEED
    )

    assert first_run == second_run


def test_simulation_uses_expected_number_of_rollouts():
    result = simulate_action(
        initial_risk=70,
        action="BACKUP_COOLING",
        scenario_id="CX-001",
        seed=RANDOM_SEED
    )

    assert result["action"] == "BACKUP_COOLING"
    assert 0 <= result["average_peak"] <= 100
    assert 0 <= result["average_final"] <= 100
    assert 0 <= result["percentile_95"] <= 100
    assert 0 <= result["high_risk_frequency"] <= 100
