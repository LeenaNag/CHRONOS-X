
import pandas as pd

from modules.temporal.reconstruction import reconstruct_scenario


def create_test_data():

    data = pd.DataFrame([
        {
            "scenario_id": "TEST-001",
            "event_id": "E003",
            "event_time": "2026-10-30 10:03:00",
            "arrival_time": "2026-10-30 10:04:00",
            "source": "sensor",
            "event_type": "temperature",
            "trust_score": 0.9,
            "component_id": "C1",
            "signature_valid": True,
        },
        {
            "scenario_id": "TEST-001",
            "event_id": "E001",
            "event_time": "2026-10-30 10:01:00",
            "arrival_time": "2026-10-30 10:05:00",
            "source": "sensor",
            "event_type": "temperature",
            "trust_score": 0.9,
            "component_id": "C1",
            "signature_valid": True,
        },
        {
            "scenario_id": "TEST-001",
            "event_id": "E002",
            "event_time": "2026-10-30 10:02:00",
            "arrival_time": "2026-10-30 10:02:30",
            "source": "sensor",
            "event_type": "temperature",
            "trust_score": 0.9,
            "component_id": "C1",
            "signature_valid": True,
        },
        {
            "scenario_id": "TEST-001",
            "event_id": "E002",
            "event_time": "2026-10-30 10:02:00",
            "arrival_time": "2026-10-30 10:06:00",
            "source": "duplicate_sensor",
            "event_type": "temperature",
            "trust_score": 0.8,
            "component_id": "C1",
            "signature_valid": True,
        },
        {
            "scenario_id": "TEST-001",
            "event_id": "E004",
            "event_time": "2026-10-30 10:07:00",
            "arrival_time": "2026-10-30 10:06:00",
            "source": "sensor",
            "event_type": "temperature",
            "trust_score": 0.9,
            "component_id": "C1",
            "signature_valid": True,
        },
    ])

    # Convert strings into datetime values before reconstruction.
    data["event_time"] = pd.to_datetime(data["event_time"])
    data["arrival_time"] = pd.to_datetime(data["arrival_time"])

    return data


def test_t1_event_time_is_chronological():

    event_history, _, _ = reconstruct_scenario(create_test_data())

    times = event_history["event_time"].tolist()

    assert times == sorted(times)


def test_t1_arrival_time_is_chronological():

    _, arrival_history, _ = reconstruct_scenario(create_test_data())

    times = arrival_history["arrival_time"].tolist()

    assert times == sorted(times)


def test_t1_duplicate_events_are_removed():

    event_history, _, duplicates = reconstruct_scenario(create_test_data())

    assert duplicates == 1
    assert len(event_history) == 4
    assert event_history["event_id"].is_unique


def test_t1_earliest_arrival_duplicate_is_kept():

    event_history, _, _ = reconstruct_scenario(create_test_data())

    duplicate_record = event_history[
        event_history["event_id"] == "E002"
    ]

    assert len(duplicate_record) == 1
    assert duplicate_record.iloc[0]["source"] == "sensor"


def test_t1_delayed_and_invalid_timing_detection():

    event_history, _, _ = reconstruct_scenario(create_test_data())

    delayed = event_history[
        event_history["event_id"] == "E003"
    ]

    invalid = event_history[
        event_history["event_id"] == "E004"
    ]

    assert delayed.iloc[0]["timing_status"] == "DELAYED"
    assert invalid.iloc[0]["timing_status"] == "INVALID_TIME"
