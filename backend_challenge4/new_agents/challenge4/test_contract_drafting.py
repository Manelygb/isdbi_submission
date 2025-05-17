import json
import sys
import os

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from challenge4.contract_drafting_agent import ContractDraftingAgent

def main():
    # Create agent
    agent = ContractDraftingAgent()
    
    # Create a test PCO with sample data
    pco = {
        "processing_log": [],
        "project_details": {
            "project_name": "Factory Construction Project",
            "sector": "Manufacturing",
            "location": "Riyadh, Saudi Arabia",
            "estimated_cost": 2000000,
            "expected_revenue": 500000,
            "payback_period": 4,
            "risks": "Construction delays; Regulatory approvals; Market demand fluctuations",
            "objective": "Construction of a specialized manufacturing facility for automotive parts"
        },
        "client_details": {
            "client_type": "company",
            "experience": "10 years in automotive manufacturing"
        },
        "project_evaluation_results": {
            "is_viable": True,
            "decision": "APPROVE",
            "confidence": 0.85,
            "justification": "The project has a strong business case with reasonable payback period and experienced management.",
            "identified_risks": [
                "Construction timeline risks",
                "Initial cash flow constraints",
                "Regulatory compliance challenges"
            ],
            "shariah_preliminary_fit": "High compatibility with Istisna'a contract structure"
        },
        "enterprise_audit_results": {
            "score": 1.75,
            "summary": "The company shows strong financial health with good liquidity and solvency ratios.",
            "key_ratios": {
                "2021": {"Current Ratio": 1.8, "Debt Ratio": 0.4},
                "2022": {"Current Ratio": 2.1, "Debt Ratio": 0.35}
            },
            "risk_level": {"Low": 2, "Moderate": 0, "High": 0},
            "verdict": "APPROVE",
            "warnings": []
        },
        "selected_contract_details": {
            "primary_contract_type": "Istisna'a",
            "justification": "Selected Istisna'a as it suits the construction project nature.",
            "key_parameters_required": ["detailed_asset_specs", "price", "delivery_schedule"],
            "relevant_aaoifi_fas": ["FAS 10"]
        },
        "current_status": "pending_contract_formalization"
    }
    
    # Execute the agent
    result = agent.execute(pco)
    
    # Print the result
    print("\n\nContract Drafting Result:")
    print(f"Status: {result['current_status']}")
    print(f"Contract Type: {result['contract_draft']['contract_type']}")
    print("\nContract Content:")
    print(result['contract_draft']['content'])
    
    # Save result to a file for inspection
    with open(os.path.join(current_dir, 'contract_draft_output.json'), 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nComplete PCO saved to '{os.path.join(current_dir, 'contract_draft_output.json')}'")

if __name__ == "__main__":
    main() 