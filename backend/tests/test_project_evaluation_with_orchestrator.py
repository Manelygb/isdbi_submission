# IMPORTANT: This test script is designed to be run from the project root directory
# (e.g., /mnt/data/hackathons/isdbi/code/) so that the imports work correctly.
# Example: python backend/tests/test_project_evaluation_with_orchestrator.py

import sys
import os

# Add the project root directory to Python's path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import json
from backend.new_agents.orchestrator import Orchestrator
from backend.new_agents.challenge4.project_evaluation_agent import ProjectEvaluationAgent

class ProjectEvaluationOrchestrator(Orchestrator):
    """A specialized orchestrator that only runs the ProjectEvaluationAgent"""
    
    def __init__(self):
        # Initialize just the ProjectEvaluationAgent, not the full chain
        self.project_evaluation_agent = ProjectEvaluationAgent()
        # Define a simplified sequence that only includes the project evaluation step
        self.agent_sequence = [
            (self.project_evaluation_agent, "pending_project_evaluation")
        ]
        # Flag to skip country law validation (not needed for this test)
        self.run_country_law_validation = False

    def _initialize_pco(self, client_details: dict, project_details: dict) -> dict:
        """Override to set the initial status to pending_project_evaluation"""
        pco = super()._initialize_pco(client_details, project_details)
        # Set status to skip enterprise audit and go directly to project evaluation
        pco["current_status"] = "pending_project_evaluation"
        # Add a mock enterprise audit result since we're skipping that step
        pco["enterprise_audit_results"] = {
            "score": 0.75,
            "summary": "Mock enterprise audit result for testing purposes.",
            "key_ratios": {},
            "risk_level": {"Low": 1, "Moderate": 1, "High": 0},
            "verdict": "APPROVE"
        }
        return pco

def run_orchestrator_test():
    print("--- Starting ProjectEvaluationAgent Test via Orchestrator ---")
    
    # Create our specialized orchestrator
    orchestrator = ProjectEvaluationOrchestrator()
    
    # 1. Test with a viable project
    print("\n=== Test Case 1: Viable Project ===")
    client_details_viable = {
        "client_name": "Green Desert Technologies",
        "client_type": "company",
        "experience": "Founded by Mohammed Al-Farsi, who has 15 years of experience in sustainable agriculture projects."
    }
    
    project_details_viable = {
        "project_name": "Solar-Powered Irrigation Network",
        "sector": "Agriculture/Renewable Energy",
        "location": "Biskra, Algeria",
        "estimated_cost": 1200000,
        "expected_revenue": 450000,
        "payback_period": 5.2,
        "risks": "Seasonal water availability; equipment maintenance in remote areas",
        "objective": "Install a network of solar-powered irrigation systems across 20 farms in the Biskra region",
        "description": "This project will use renewable energy to power irrigation systems in an arid region, reducing water usage by 40% while improving crop yields."
    }
    
    print("Processing viable project...")
    result_viable = orchestrator.process_project(client_details_viable, project_details_viable)
    
    print("\nResults for Viable Project:")
    print(f"Final Status: {result_viable['current_status']}")
    if 'project_evaluation_results' in result_viable and result_viable['project_evaluation_results']:
        print(json.dumps(result_viable['project_evaluation_results'], indent=2))
    else:
        print("No evaluation results generated.")
    
    # 2. Test with a risky project that should likely be rejected
    print("\n\n=== Test Case 2: High-Risk Project ===")
    client_details_risky = {
        "client_name": "Desert Innovations LLC",
        "client_type": "company",
        "experience": "New company with no previous project experience. CEO has background in theoretical physics."
    }
    
    project_details_risky = {
        "project_name": "Experimental Atmospheric Water Harvesting",
        "sector": "Water Technology",
        "location": "Deep Sahara Desert",
        "estimated_cost": 8500000,
        "expected_revenue": 350000,
        "payback_period": 24.3,
        "risks": "Unproven technology; extreme climate conditions; remote location accessibility; high maintenance costs; uncertain government permits; technology reliability concerns",
        "objective": "Deploy experimental atmospheric water harvesting devices using novel materials in extreme desert conditions",
        "description": "This frontier-science project aims to extract water directly from air in the world's most arid desert environment using breakthrough materials science."
    }
    
    print("Processing high-risk project...")
    result_risky = orchestrator.process_project(client_details_risky, project_details_risky)
    
    print("\nResults for High-Risk Project:")
    print(f"Final Status: {result_risky['current_status']}")
    if 'project_evaluation_results' in result_risky and result_risky['project_evaluation_results']:
        print(json.dumps(result_risky['project_evaluation_results'], indent=2))
    else:
        print("No evaluation results generated.")
    
    # 3. Test with a project that needs modification
    print("\n\n=== Test Case 3: Project Needing Modification ===")
    client_details_modify = {
        "client_name": "AlgHydro Solutions",
        "client_type": "company",
        "experience": "5 years in water management, but first time implementing in agricultural setting."
    }
    
    project_details_modify = {
        "project_name": "Hydroponic Desert Farm",
        "sector": "Agriculture",
        "location": "Ouargla, Algeria",
        "estimated_cost": 3200000,
        "expected_revenue": 700000,
        "payback_period": 8.1,
        "risks": "High initial costs; energy requirements; specialized staff needs; market acceptance for hydroponic produce",
        "objective": "Establish a large-scale hydroponic farm in the desert to grow premium crops",
        "description": "This project will create a 5-hectare hydroponic facility using groundwater and solar energy to grow high-value crops for export markets."
    }
    
    print("Processing project needing modification...")
    result_modify = orchestrator.process_project(client_details_modify, project_details_modify)
    
    print("\nResults for Project Needing Modification:")
    print(f"Final Status: {result_modify['current_status']}")
    if 'project_evaluation_results' in result_modify and result_modify['project_evaluation_results']:
        print(json.dumps(result_modify['project_evaluation_results'], indent=2))
    else:
        print("No evaluation results generated.")
    
    print("\n--- Orchestrator Test Finished ---")

if __name__ == "__main__":
    run_orchestrator_test() 