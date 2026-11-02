
from fastapi import FastAPI, HTTPException
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.pipeline import load_all_data, run_pipeline

app = FastAPI(
    title="CHRONOS-X API",
    description="Industrial Risk Intelligence and Decision Support Prototype",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "project": "CHRONOS-X",
        "status": "online",
        "message": "CHRONOS-X API is running"
    }


@app.get("/scenarios")
def get_scenarios():
    try:
        data = load_all_data()
        scenarios = sorted(
            data["scenario_id"].dropna().unique().tolist()
        )

        return {
            "total_scenarios": len(scenarios),
            "scenarios": scenarios
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


@app.get("/analyze/{scenario_id}")
def analyze_scenario(scenario_id: str):
    try:
        result = run_pipeline(scenario_id)

        simulations = [
            {
                "action": item["action"],
                "objective_score": float(item["objective_score"]),
                "percentile_95": float(item["percentile_95"])
            }
            for item in result["m3"]["results"]
        ]

        return {
            "scenario_id": result["scenario_id"],

            "temporal_reconstruction": {
                "event_count": len(result["m1"]["event_history"]),
                "arrival_count": len(result["m1"]["arrival_history"]),
                "duplicates": result["m1"]["duplicates"]
            },

            "causal_investigation": {
                "root_cause": result["m2"]["root_cause"],
                "hypotheses": result["m2"]["hypotheses"]
            },

            "counterfactual_simulation": {
                "best_option": result["m3"]["best_simulated_option"],
                "results": simulations
            },

            "optimization": {
                "plan": result["m5"]["optimized"]["plan"],
                "feasible": bool(result["m5"]["feasible"])
            },

            "adversarial_detection": {
                "records_analyzed": len(result["m6"]),
                "flagged_records": int(
                    (result["m6"]["detection_status"] == "REVIEW_REQUIRED").sum()
                )
            },

            "safety_verification": {
                "status": result["m7"]["status"],
                "actions": result["m7"]["actions"],
                "reasons": result["m7"]["reasons"]
            },

            "disclaimer": (
                "Synthetic prototype results only. "
                "Not real-world industrial operating instructions."
            )
        }

    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

