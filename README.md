# CHRONOS-X
## Industrial Risk Intelligence and Decision Support Prototype

CHRONOS-X is a research prototype developed for a 24-hour national-level inter-college hackathon at MIT Engineering College, Mysuru.

It analyzes synthetic industrial event data, investigates possible root causes, simulates alternative outcomes, detects suspicious records, and evaluates proposed actions using safety checks.

**Important:** This is an academic decision-support prototype. It is not connected to real industrial equipment and must not be used to control real facilities.

---

## 1. Main Features

| Module | Description |
|---|---|
| M1 – Temporal Reconstruction | Organizes events using event time and arrival time, handles delayed and duplicate records. |
| M2 – Causal Investigation | Generates possible root-cause hypotheses. |
| M3 – Counterfactual Simulation | Compares alternative actions using repeated simulated outcomes. |
| M4 – Multi-Agent Analysis | Uses different analytical roles to review the situation. |
| M5 – Risk Optimization | Evaluates action plans against risk, resources, and time constraints. |
| M6 – Adversarial Detection | Flags suspicious, inconsistent, or potentially manipulated records. |
| M7 – Safety Verification | Checks proposed actions and reports PASS, FAIL, or UNKNOWN. |
| M8 – Time-Travel Dashboard | Provides an interactive view of historical and incoming events. |

---

## 2. Technology Stack

- Python 3.12
- Pandas and NumPy
- Scikit-learn
- NetworkX
- SimPy
- FastAPI
- Streamlit
- Plotly
- Pytest
- Hypothesis

---

## 3. Project Structure

```text
CHRONOS-X/
│
├── api/
│   ├── requests.http
│   └── sample_cx006_response.json
│
├── backend/
│   ├── main.py
│   └── pipeline.py
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── chronos_x_events.csv
│   ├── chronos_x_scenarios.json
│   └── paradox_protocol/
│       └── cx006_events.csv
│
├── modules/
│   ├── temporal/
│   ├── causal/
│   ├── simulation/
│   ├── agents/
│   ├── optimization/
│   ├── security/
│   └── safety/
│
├── tests/
│   ├── test_challenge_t1.py
│   ├── test_challenge_t2.py
│   ├── test_challenge_t3.py
│   ├── test_properties.py
│   └── test_system.py
│
├── requirements.txt
└── README.md
```

---

## 4. Installation

Clone or download the project and open its root folder in VS Code.

### Step 1: Create a virtual environment

```powershell
python -m venv .venv
```

### Step 2: Activate the environment

```powershell
.venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```powershell
python -m pip install -r requirements.txt
```

---

## 5. Run the Backend API

From the project root, execute:

```powershell
uvicorn backend.main:app --reload
```

API address:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### Available API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Check API status |
| GET | `/scenarios` | List available scenarios |
| GET | `/analyze/CX-006` | Analyze scenario CX-006 |

---

## 6. Run the Dashboard

Open another VS Code terminal.

Activate the virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

Run the dashboard:

```powershell
streamlit run dashboard/app.py
```

The interactive dashboard will open in your browser.

---

## 7. Run Automated Tests

Run all project tests:

```powershell
python -m pytest -v
```

Run only property-based tests:

```powershell
python -m pytest tests/test_properties.py -v
```

### Latest Verified Test Results

- Total tests: 23
- Passed: 23
- Failed: 0

The project uses:
- **Pytest:** Automated functional and system testing.
- **Hypothesis:** Property-based testing with generated input values.

---

## 8. Synthetic Scenarios

The project currently includes six scenarios.

| Scenario | Description |
|---|---|
| CX-001 | Cooling degradation |
| CX-002 | Spoofed temperature sensor |
| CX-003 | Network intrusion and control disruption |
| CX-004 | Conflicting maintenance report |
| CX-005 | Delayed secondary effect and mechanical degradation |
| CX-006 | Paradox Protocol |

All scenario records and values are synthetic and illustrative.

---

## 9. Counterfactual Simulation Configuration

The M3 simulation module uses Monte Carlo simulation to compare alternative actions.

### Simulation Settings

| Parameter | Configuration |
|---|---:|
| Base random seed | 42 |
| Monte Carlo rollouts | 200 |
| Simulation steps per rollout | 10 |
| Random generator | NumPy default_rng |
| Base risk index | Illustrative value |
| Risk range | 0–100 |

### Reproducibility

The simulation uses a fixed base random seed:

```python
RANDOM_SEED = 42
```

Scenario and action seeds are derived from this base seed.

Using the same input data, code, and seed settings produces reproducible simulation results.

The simulation models illustrative assumptions and does not represent real-world industrial probabilities.

---

## 10. API Example

Example request:

```http
GET http://127.0.0.1:8000/analyze/CX-006
```

The API response includes:

- Temporal reconstruction
- Root-cause hypotheses
- Counterfactual simulation results
- Optimization plan
- Adversarial detection results
- Safety verification status

A sample response is available at:

```text
api/sample_cx006_response.json
```

API requests are documented in:

```text
api/requests.http
```

---

## 11. Known Limitations

- The dataset contains synthetic records, not real industrial telemetry.
- Causal hypotheses are prototype estimates, not proven causes.
- Simulation outcomes depend on simplified assumptions.
- Adversarial detection flags require human review.
- A PASS status does not represent industrial safety certification.
- UNKNOWN means available evidence is insufficient for a confident decision.
- The prototype does not directly control industrial equipment.
- External simulator integration and additional validation are future improvements.

---

## 12. Future Improvements

- Integration with a validated external simulator.
- More advanced causal discovery.
- Improved adversarial detection.
- Expanded safety verification.
- More comprehensive benchmark and ablation studies.
- Improved dashboard visualizations.

---

## 13. Disclaimer

CHRONOS-X is an academic research prototype developed for hackathon demonstration and evaluation.

All scenarios, event records, and simulated outcomes are illustrative. This prototype is not a certified industrial safety system and must not be used as a substitute for professional engineering assessment or operational safety procedures.

