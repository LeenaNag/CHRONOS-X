
from datetime import datetime


class InvestigatorAgent:

    def investigate(self, scenario_id, root_cause):
        return {
            "agent": "Investigator",
            "scenario": scenario_id,
            "finding": root_cause,
            "status": "INVESTIGATION_COMPLETED"
        }


class PredictorAgent:

    def predict(self, simulation_results):

        if not simulation_results:
            return {
                "agent": "Predictor",
                "finding": "Insufficient simulation data.",
                "status": "INSUFFICIENT_DATA"
            }

        best_result = min(
            simulation_results,
            key=lambda item: float(item.get("objective_score", float("inf")))
        )

        worst_result = max(
            simulation_results,
            key=lambda item: float(item.get("objective_score", float("-inf")))
        )

        predictions = []

        for result in simulation_results:
            predictions.append({
                "action": result.get("action", "UNKNOWN"),
                "objective_score": result.get("objective_score"),
                "average_final": result.get("average_final", "Not available"),
                "percentile_95": result.get("percentile_95", "Not available"),
                "high_risk_frequency": result.get(
                    "high_risk_frequency", "Not available"
                )
            })

        return {
            "agent": "Predictor",
            "finding": "Simulation outcomes analysed successfully.",
            "best_predicted_action": best_result.get("action"),
            "best_objective_score": best_result.get("objective_score"),
            "highest_objective_action": worst_result.get("action"),
            "total_actions_analysed": len(simulation_results),
            "predictions": predictions,
            "status": "PREDICTION_COMPLETED"
        }


class OptimizerAgent:

    def optimize(self, simulation_results):

        if not simulation_results:
            return {
                "agent": "Optimizer",
                "recommendation": "NO_RECOMMENDATION",
                "status": "INSUFFICIENT_DATA"
            }

        best = min(
            simulation_results,
            key=lambda item: float(item["objective_score"])
        )

        return {
            "agent": "Optimizer",
            "recommendation": best["action"],
            "objective_score": best["objective_score"],
            "status": "OPTION_IDENTIFIED"
        }


class SafetyAgent:

    def verify(self, recommendation):

        if not recommendation:
            return {
                "agent": "Safety",
                "decision": "UNKNOWN",
                "reason": "No recommendation available."
            }

        return {
            "agent": "Safety",
            "decision": "REQUIRES_VALIDATION",
            "reason": (
                "Recommendation must pass M7 safety "
                "verification before approval."
            )
        }


class RedTeamAgent:

    def challenge(self, evidence):

        warnings = []
        checks_performed = []

        if not evidence:
            warnings.append("No supporting evidence provided.")
        else:
            checks_performed.append("Supporting evidence availability")

        simulations = evidence.get("simulation_results", [])

        if not simulations:
            warnings.append("No simulation results available.")
        else:
            checks_performed.append("Simulation results availability")

            for result in simulations:

                action = result.get("action", "UNKNOWN")

                score = result.get("objective_score")

                if score is None:
                    warnings.append(
                        f"{action}: Objective score is missing."
                    )

                if result.get("high_risk_frequency") is None:
                    warnings.append(
                        f"{action}: High-risk frequency is not available."
                    )

        if not evidence.get("root_cause"):
            warnings.append("Root-cause finding is missing.")
        else:
            checks_performed.append("Root-cause finding availability")

        if warnings:
            status = "WARNINGS_FOUND"
        else:
            status = "NO_ISSUES_DETECTED_BY_BASIC_CHECKS"

        return {
            "agent": "Red Team",
            "checks_performed": checks_performed,
            "warnings": warnings,
            "warning_count": len(warnings),
            "status": status
        }


class MultiAgentOrchestrator:

    def __init__(self):
        self.investigator = InvestigatorAgent()
        self.predictor = PredictorAgent()
        self.optimizer = OptimizerAgent()
        self.safety = SafetyAgent()
        self.red_team = RedTeamAgent()

    def run(self, scenario_id, root_cause, simulation_results):

        investigation = self.investigator.investigate(
            scenario_id, root_cause
        )

        prediction = self.predictor.predict(
            simulation_results
        )

        optimization = self.optimizer.optimize(
            simulation_results
        )

        safety_check = self.safety.verify(
            optimization.get("recommendation")
        )

        red_team_evidence = {
            "root_cause": root_cause,
            "simulation_results": simulation_results
        }

        red_team_review = self.red_team.challenge(
            red_team_evidence
        )

        return {
            "scenario": scenario_id,
            "timestamp": datetime.now().isoformat(),
            "investigation": investigation,
            "prediction": prediction,
            "optimization": optimization,
            "safety": safety_check,
            "red_team": red_team_review,
            "final_status": "AWAITING_M7_VERIFICATION"
        }


if __name__ == "__main__":

    orchestrator = MultiAgentOrchestrator()

    sample_results = [
        {
            "action": "BACKUP_COOLING",
            "objective_score": 47.78,
            "average_final": 42.5,
            "percentile_95": 52.39,
            "high_risk_frequency": 0.10
        },
        {
            "action": "REDUCE_MACHINE_LOAD",
            "objective_score": 54.10,
            "average_final": 49.2,
            "percentile_95": 61.30,
            "high_risk_frequency": 0.20
        },
        {
            "action": "NO_ACTION",
            "objective_score": 65.22,
            "average_final": 60.1,
            "percentile_95": 74.18,
            "high_risk_frequency": 0.40
        }
    ]

    result = orchestrator.run(
        scenario_id="CX-001",
        root_cause="Cooling system degradation",
        simulation_results=sample_results
    )

    print("\n========== CHRONOS-X M4 ==========")

    for agent, output in result.items():
        print(f"\n{agent.upper()}:")
        print(output)

    print("\nM4 MULTI-AGENT SYSTEM COMPLETED")
