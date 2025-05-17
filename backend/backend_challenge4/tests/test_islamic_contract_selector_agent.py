# IMPORTANT: This test script is designed to be run from the project root directory
# (e.g., /mnt/data/hackathons/isdbi/code/) so that the imports work correctly.
# Example: python backend/tests/test_islamic_contract_selector_agent.py

import sys
import os

# Add the project root directory to Python's path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import json
# Ensure the agent can be imported from its location within the backend package.
from backend.new_agents.challenge4.islamic_contract_selector_agent import IslamicContractSelectorAgent

# python-dotenv is loaded within the agent itself.
# Ensure your .env file (with OPENROUTER_API_KEY) is in a discoverable path
# (e.g., project root or current working directory when running this script).

def run_islamic_contract_selector_test():
    print("--- Starting IslamicContractSelectorAgent Test ---")

    # 1. Construct a detailed sample PCO
    sample_pco = {
        "pco_id": "PCO_TEST_CONTRACT_001",
        "project_details": {
            "project_name": "Al-Baraka Commercial Complex Development",
            "sector": "Real Estate Construction",
            "location": "Dubai, UAE",
            "estimated_cost": 15000000,
            "expected_revenue": 2000000,
            "payback_period": 8,
            "objective": "Construction of a multi-use commercial center with retail, office, and restaurant spaces according to custom specifications. The client requires complete construction from foundation to finishing.",
            "risks": "Market volatility; Construction delays; Regulatory changes; Competition from nearby developments",
            "project_timeline": "24 months for construction phase followed by operational phase",
            "project_type": "Construction of new physical asset with specific custom requirements",
            "asset_ownership": "Asset will be owned by client after construction completion"
        },
        "client_details": {
            "client_type": "company",
            "experience": "10+ years in real estate development with 3 similar projects completed",
            "financing_needs": "Full financing for construction phase with deferred payment capability",
            "financial_data_csv": """Year,CurrentAssets,CurrentLiabilities,StocksAndRelief,IssuedCapital,TotalLiabilities,TotalAssets,NetIncome,Revenue,PermanentCapital,FixedAssets,NonCurrentAssets
2021,5000000,2500000,500000,10000000,7500000,20000000,1800000,4500000,15000000,12000000,15000000
2022,5500000,2800000,550000,10000000,8000000,22000000,2000000,5000000,16000000,13000000,16500000
2023,6000000,3000000,600000,10000000,9000000,25000000,2200000,5500000,17000000,14000000,19000000"""
        },
        "enterprise_audit_results": {
            "score": 1.65,
            "summary": "The company demonstrates strong financial health with steady growth in assets and revenue over the past three years. Liquidity ratios are within acceptable ranges, and debt levels are manageable relative to equity. Cash flow generation has been consistent, providing good coverage for planned expansion.",
            "key_ratios": {
                "2023": {
                    "Current Ratio": 2.0,
                    "Quick Ratio": 1.8,
                    "Debt Ratio": 0.36,
                    "Return on Assets": 0.088,
                    "Return on Equity": 0.22
                }
            },
            "risk_level": {"Low": 2, "Moderate": 1, "High": 0},
            "verdict": "APPROVE",
            "warnings": []
        },
        "project_evaluation_results": {
            "is_viable": True,
            "decision": "APPROVE",
            "confidence": 0.88,
            "justification": "The project demonstrates strong commercial viability with reasonable payback period. The developer has proven experience in similar projects and maintains good financial health. Market demand for commercial space in the target area remains strong despite some competition.",
            "identified_risks": [
                "Construction cost overruns possible due to supply chain issues",
                "Potential delays in regulatory approvals",
                "Market saturation in premium commercial space"
            ],
            "shariah_preliminary_fit": "Project involves constructing a custom commercial building according to specified requirements, with delivery expected after completion. This aligns well with Istisna'a (manufacturing/construction contract) as the primary structure, with potential for Ijarah (lease) arrangement post-completion. FAS 10 and SS 11 would be applicable."
        },
        "processing_log": [
            {"agent": "SystemInitializer", "timestamp": "2024-05-22T10:00:00Z", "message": "PCO initiated for Islamic Contract Selection.", "status": "started"}
        ],
        "current_status": "pending_contract_selection"
    }

    print(f"Sample PCO ID: {sample_pco['pco_id']}")
    print(f"Project Name: {sample_pco['project_details']['project_name']}")
    print(f"Project Sector: {sample_pco['project_details']['sector']}")

    # 2. Instantiate the agent
    agent = None
    try:
        # The IslamicContractSelectorAgent's __init__ loads .env, embeddings, FAISS.
        # Its internal vector_store_path is relative to the agent's own file location.
        agent = IslamicContractSelectorAgent()
        print(f"Successfully instantiated {agent.agent_name}.")
    except FileNotFoundError as fnf_error:
        print(f"ERROR Instantiating Agent: {fnf_error}")
        print("Note: Vector store not found is a non-critical error; the agent will proceed with built-in knowledge.")
    except ValueError as val_error:
        print(f"ERROR Instantiating Agent: {val_error}")
        print("Ensure OPENROUTER_API_KEY is set in your .env file (accessible from the project root).")
        return
    except Exception as e:
        print(f"An unexpected error occurred during agent instantiation: {e}")
        return

    # 3. Perform the task
    print(f"Calling _perform_task for agent: {agent.agent_name}...")
    try:
        agent._perform_task(sample_pco)  # The agent modifies sample_pco in-place
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
        print(f"  Agent: {log_entry.get('agent', 'Unknown')}")
        print(f"  Message: {log_entry.get('message', 'No message')}")
        print("-" * 20)

    print("\nSelected Contract Details:")
    contract_details = sample_pco.get("selected_contract_details")
    if contract_details:
        # Pretty print the JSON report
        print(json.dumps(contract_details, indent=4, ensure_ascii=False))
        
        # Highlight the primary contract selected
        print(f"\nPrimary Contract Selected: {contract_details.get('primary_contract_type', 'Unknown')}")
        
        # Show probabilities if available
        if 'contract_probabilities' in contract_details:
            print("\nContract Probabilities:")
            for contract, probability in contract_details['contract_probabilities'].items():
                print(f"  {contract}: {probability:.2f}")
    else:
        print("No contract selection details were generated in the PCO.")
    
    print("\n--- Test Script Finished ---")

if __name__ == "__main__":
    run_islamic_contract_selector_test() 