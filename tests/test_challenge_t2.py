
import pandas as pd

from modules.causal.root_cause import (
    investigate_scenario,
    detect_conflicting_reports
)


def create_conflicting_data():

    data = pd.DataFrame([
        {
            "scenario_id": "TEST-T2",
            "event_id": "T2-E001",
            "event_time": "2026-10-30 10:00:00",
            "arrival_time": "2026-10-30 10:01:00",
            "source": "cooling_sensor",
            "event_type": "cooling_status",
            "value": "ACTIVE",
            "trust_score": 0.95,
            "signature_valid": True
        },
        {
            "scenario_id": "TEST-T2",
            "event_id": "T2-E002",
            "event_time": "2026-10-30 10:00:30",
            "arrival_time": "2026-10-30 10:02:00",
            "source": "maintenance_system",
            "event_type": "cooling_status",
            "value": "INACTIVE",
            "trust_score": 0.85,
            "signature_valid": True
        },
        {
            "scenario_id": "TEST-T2",
            "event_id": "T2-E003",
            "event_time": "2026-10-30 10:03:00",
            "arrival_time": "2026-10-30 10:04:00",
            "source": "temperature_sensor",
            "event_type": "temperature",
            "value": "85",
            "trust_score": 0.90,
            "signature_valid": True
        }
    ])

    data["event_time"] = pd.to_datetime(data["event_time"])
    data["arrival_time"] = pd.to_datetime(data["arrival_time"])

    data["numeric_value"] = pd.to_numeric(
        data["value"], errors="coerce"
    )

    return data


def test_t2_detects_conflicting_cooling_reports():

    data = create_conflicting_data()

    conflicts = detect_conflicting_reports(data)

    cooling_conflicts = [
        item for item in conflicts
        if item["event_type"] == "cooling_status"
    ]

    assert len(cooling_conflicts) == 1


def test_t2_preserves_both_reported_values():

    data = create_conflicting_data()

    conflicts = detect_conflicting_reports(data)

    cooling_conflict = next(
        item for item in conflicts
        if item["event_type"] == "cooling_status"
    )

    assert set(cooling_conflict["reported_values"]) == {
        "ACTIVE",
        "INACTIVE"
    }


def test_t2_identifies_reporting_sources():

    data = create_conflicting_data()

    conflicts = detect_conflicting_reports(data)

    cooling_conflict = next(
        item for item in conflicts
        if item["event_type"] == "cooling_status"
    )

    assert set(cooling_conflict["sources"]) == {
        "cooling_sensor",
        "maintenance_system"
    }


def test_t2_creates_conflict_hypothesis():

    data = create_conflicting_data()

    hypotheses, graph = investigate_scenario(data)

    conflict_hypotheses = [
        item for item in hypotheses
        if item["cause"] == "Conflicting cooling-system reports"
    ]

    assert len(conflict_hypotheses) == 1

    assert conflict_hypotheses[0]["score"] == 85

    assert graph.number_of_nodes() > 0


def test_t2_does_not_flag_single_report_as_conflict():

    data = create_conflicting_data()

    data = data[
        data["event_type"] != "cooling_status"
    ]

    conflicts = detect_conflicting_reports(data)

    assert conflicts == []
