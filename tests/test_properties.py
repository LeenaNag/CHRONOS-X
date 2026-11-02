
import pandas as pd
from hypothesis import given, settings
from hypothesis import strategies as st

from modules.temporal.reconstruction import reconstruct_scenario


@settings(max_examples=30, deadline=None)
@given(
    values=st.lists(
        st.integers(min_value=0, max_value=1000),
        min_size=1,
        max_size=30,
        unique=True
    )
)
def test_event_history_is_chronological(values):
    base = pd.Timestamp("2026-01-01 10:00:00")

    data = pd.DataFrame({
        "scenario_id": ["TEST"] * len(values),
        "event_id": [f"E{i}" for i in range(len(values))],
        "event_time": [base + pd.Timedelta(seconds=v) for v in values],
        "arrival_time": [base + pd.Timedelta(seconds=v + 5) for v in values],
        "source": ["sensor"] * len(values),
        "event_type": ["temperature"] * len(values),
        "value": values,
        "unit": ["C"] * len(values),
        "trust_score": [0.9] * len(values),
        "component_id": ["C1"] * len(values),
        "signature_valid": [True] * len(values),
        "note": ["test"] * len(values)
    })

    event_history, arrival_history, duplicates = reconstruct_scenario(data)

    event_times = pd.to_datetime(event_history["event_time"])
    arrival_times = pd.to_datetime(arrival_history["arrival_time"])

    assert event_times.is_monotonic_increasing
    assert arrival_times.is_monotonic_increasing
    assert len(event_history) == len(values)


@settings(max_examples=20, deadline=None)
@given(
    count=st.integers(min_value=1, max_value=20)
)
def test_duplicate_events_do_not_increase_history(count):
    base = pd.Timestamp("2026-01-01 10:00:00")

    row = {
        "scenario_id": "TEST",
        "event_id": "E001",
        "event_time": base,
        "arrival_time": base + pd.Timedelta(seconds=5),
        "source": "sensor",
        "event_type": "temperature",
        "value": 50,
        "unit": "C",
        "trust_score": 0.9,
        "component_id": "C1",
        "signature_valid": True,
        "note": "test"
    }

    data = pd.DataFrame([row.copy() for _ in range(count)])

    event_history, arrival_history, duplicates = reconstruct_scenario(data)

    assert len(event_history) == 1
    assert len(arrival_history) == 1
    assert duplicates == count - 1
