# IMPORTANT: This test script is designed to be run from the project root directory
# (e.g., /mnt/data/hackathons/isdbi/code/) so that the imports work correctly.
# Example: python backend/tests/test_project_evaluation_agent.py

import sys
import os

# Add the project root directory to Python's path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import json
# Ensure the agent can be imported from its location within the backend package.
from backend.new_agents.challenge4.project_evaluation_agent import ProjectEvaluationAgent

# python-dotenv is loaded within the agent itself.
# Ensure your .env file (with API keys) is in a discoverable path
# (e.g., project root or current working directory when running this script).

def run_project_evaluation_agent_test():
    print("--- Starting ProjectEvaluationAgent Test ---")

    # 1. Construct a detailed sample PCO
    sample_pco = {
        "pco_id": "PCO_TEST_PROJECT_EVAL_001",
        "client_details": {
            "client_name": "Sahara Green Innovations",
            "client_type": "company",
            "registration_number": "987654321",
            "incorporation_date": "2018-07-12",
            "industry_sector": "Sustainable Agriculture",
            "legal_form": "Limited Company",
            "ownership_structure": {
                "major_shareholders": [
                    {"name": "Tariq Mansour", "ownership_percentage": 55},
                    {"name": "Sustainable Investments LLC", "ownership_percentage": 45}
                ]
            },
            "experience": "Tariq has 10+ years in sustainable agriculture and has completed two similar projects in Morocco."
        },
        "project_details": {
            "project_name": "Desert Smart Irrigation System",
            "sector": "Agriculture",
            "location": "Ghardaia, Algeria",
            "estimated_cost": 750000,
            "expected_revenue": 300000,
            "payback_period": 4.5,
            "risks": "Water access limitations; unproven technology in extreme desert conditions; regulatory approvals pending",
            "objective": "Implement a smart drip irrigation system using renewable energy to cultivate drought-resistant crops in desert regions.",
            "description": "This project aims to transform 100 hectares of arid land into productive agricultural land using advanced water-saving technology and solar power.",
            "duration_months": 18
        },
        "enterprise_audit_results": {
            "score": 0.82,
            "summary": "Company shows solid financial health with moderate risk profile.",
            "key_ratios": {},
            "risk_level": {
                "Low": 1,
                "Moderate": 2,
                "High": 0
            },
            "verdict": "APPROVE",
            "warnings": []
        },
        "processing_log": [
            {"agent": "Orchestrator", "timestamp": "2024-05-22T09:00:00Z", "message": "PCO initiated for testing.", "status": "system"},
            {"agent": "EnterpriseAuditAgent", "timestamp": "2024-05-22T09:01:00Z", "message": "Company financial audit completed successfully.", "status": "completed"}
        ],
        "current_status": "pending_project_evaluation"
    }

    print(f"Sample PCO ID: {sample_pco['pco_id']}")
    print(f"Client Name: {sample_pco['client_details']['client_name']}")
    print(f"Project Name: {sample_pco['project_details']['project_name']}")

    # 2. Instantiate the agent
    agent = None
    try:
        # The ProjectEvaluationAgent's __init__ loads .env and initializes the LLM and vector store.
        agent = ProjectEvaluationAgent()
        print(f"Successfully instantiated {agent.agent_name}.")
    except FileNotFoundError as fnf_error:
        print(f"ERROR Instantiating Agent: {fnf_error}")
        print("Warning about missing vector store is expected in test environment.")
        # Continue execution even if vector store is missing
        agent = ProjectEvaluationAgent()
    except ValueError as val_error:
        print(f"ERROR Instantiating Agent: {val_error}")
        print("Ensure API keys are set in your .env file (accessible from the project root).")
        return
    except Exception as e:
        print(f"An unexpected error occurred during agent instantiation: {e}")
        return

    # 3. Perform the task
    print(f"Calling _perform_task for agent: {agent.agent_name}...")
    try:
        agent._perform_task(sample_pco) # The agent modifies sample_pco in-place
    except Exception as e:
        # The agent's _perform_task has its own try-except block that should populate
        # the report with an error. This catch is for unexpected errors bubbling up.
        print(f"CRITICAL ERROR during agent's _perform_task: {e}")
        print("The agent's internal error handling might have already set an error status in the PCO.")

    # 4. Display results
    print("\n--- Agent Task Execution Summary ---")
    print(f"PCO Current Status: {sample_pco.get('current_status')}")

    print("\nProcessing Log:")
    for log_entry in sample_pco.get("processing_log", []):
        print(f"  Agent: {log_entry.get('agent')}")
        print(f"  Message: {log_entry.get('message')}")
        print("-" * 20)

    print("\nProject Evaluation Results:")
    eval_results = sample_pco.get("project_evaluation_results")
    if eval_results:
        # Pretty print the JSON report
        print(json.dumps(eval_results, indent=4, ensure_ascii=False))
    else:
        print("No evaluation results were generated in the PCO.")
    
    # 5. Test with a risky project (high payback period, low revenue-to-cost ratio)
    print("\n--- Testing with risky project ---")
    risky_pco = sample_pco.copy()
    risky_pco["project_details"] = {
        "project_name": "Experimental Desert Wind Farm",
        "sector": "Renewable Energy",
        "location": "Remote Sahara, Algeria",
        "estimated_cost": 5000000,
        "expected_revenue": 400000,  # Only 8% revenue-to-cost ratio
        "payback_period": 15.5,  # Very long payback period
        "risks": "Extreme desert conditions; unproven wind patterns; remote location maintenance challenges; grid connection difficulties; equipment import complications",
        "objective": "Test experimental wind turbines designed for low wind speeds in desert conditions.",
        "description": "This project aims to test and validate new wind turbine designs in extreme desert conditions with unpredictable wind patterns.",
        "duration_months": 36
    }
    risky_pco["processing_log"].append({
        "agent": "Orchestrator", 
        "timestamp": "2024-05-22T10:00:00Z", 
        "message": "Starting risky project evaluation test.", 
        "status": "system"
    })
    
    try:
        agent._perform_task(risky_pco)
        print(f"Risky project test - PCO Status: {risky_pco.get('current_status')}")
        print("Risky project test - Evaluation Results:")
        print(json.dumps(risky_pco.get("project_evaluation_results", {}), indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"CRITICAL ERROR during risky project test: {e}")
    
    # 6. Test with missing project details
    print("\n--- Testing with missing project details ---")
    missing_details_pco = sample_pco.copy()
    missing_details_pco.pop("project_details")
    missing_details_pco["processing_log"] = [
        {"agent": "Orchestrator", "timestamp": "2024-05-22T11:00:00Z", "message": "Starting test with missing project details.", "status": "system"}
    ]
    
    try:
        agent._perform_task(missing_details_pco)
        print(f"Missing details test - PCO Status: {missing_details_pco.get('current_status')}")
        print("Missing details test - Evaluation Results:")
        print(json.dumps(missing_details_pco.get("project_evaluation_results", {}), indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"CRITICAL ERROR during missing details test: {e}")

    print("\n--- Test Script Finished ---")

if __name__ == "__main__":
    run_project_evaluation_agent_test() 