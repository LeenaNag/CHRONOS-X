
import pandas as pd

from modules.causal.root_cause import assess_confounding_risk


def test_detects_possible_unobserved_confounding():
    data = pd.DataFrame({
        "event_type": ["temperature", "coolant_flow"]
    })

    result = assess_confounding_risk(data)

    assert len(result) == 1
    assert result[0]["status"] == "POSSIBLE_NOT_CONFIRMED"
    assert "unobserved" in result[0]["cause"].lower()


def test_detects_available_operating_condition():
    data = pd.DataFrame({
        "event_type": [
            "temperature",
            "coolant_flow",
            "machine_load"
        ]
    })

    result = assess_confounding_risk(data)

    assert len(result) == 1
    assert result[0]["status"] == "REQUIRES_FURTHER_ANALYSIS"


def test_no_finding_without_temperature():
    data = pd.DataFrame({
        "event_type": ["coolant_flow", "machine_load"]
    })

    result = assess_confounding_risk(data)

    assert result == []


def test_no_finding_without_coolant_flow():
    data = pd.DataFrame({
        "event_type": ["temperature", "machine_load"]
    })

    result = assess_confounding_risk(data)

    assert result == []


def test_missing_operating_variables_are_reported():
    data = pd.DataFrame({
        "event_type": ["temperature", "coolant_flow"]
    })

    result = assess_confounding_risk(data)

    assert len(result) == 1
    assert "machine_load" in result[0]["missing_variables"]
