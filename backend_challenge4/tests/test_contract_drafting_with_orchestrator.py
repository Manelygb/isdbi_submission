# IMPORTANT: This test script is designed to be run from the project root directory
# (e.g., /mnt/data/hackathons/isdbi/code/) so that the imports work correctly.
# Example: python backend/tests/test_contract_drafting_with_orchestrator.py

import sys
import os
import datetime

# Add the project root directory to Python's path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import json
try:
    from backend.new_agents.orchestrator import Orchestrator
    from backend.new_agents.challenge4.contract_drafting_agent import ContractDraftingAgent
    from backend.new_agents.challenge4.base_agent import BaseAgent
except ImportError:
    # Alternative import paths if running from different location
    from new_agents.orchestrator import Orchestrator
    from new_agents.challenge4.contract_drafting_agent import ContractDraftingAgent
    from new_agents.challenge4.base_agent import BaseAgent

# Ensure outputs directory exists
OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), 'outputs')
os.makedirs(OUTPUTS_DIR, exist_ok=True)

class MockIslamicContractSelectorAgent(BaseAgent):
    """Mock agent to simulate contract selection step"""
    agent_name = "MockIslamicContractSelectorAgent"

    def _perform_task(self, pco: dict):
        contract_type = pco.get("_test_contract_type", "Istisna'a")
        fas_standard = "FAS 10"
        
        if contract_type == "Murabaha":
            fas_standard = "FAS 2"
        elif contract_type == "Musharakah":
            fas_standard = "FAS 7"
        
        pco["selected_contract_details"] = {
            "primary_contract_type": contract_type,
            "justification": f"Selected {contract_type} as it suits the project nature (mocked for testing).",
            "key_parameters_required": ["detailed_asset_specs", "price", "delivery_schedule"],
            "relevant_aaoifi_fas": [fas_standard]
        }
        pco["current_status"] = "pending_contract_formalization"
        pco["processing_log"][-1]["message"] = f"Contract type {contract_type} selected."

class ContractDraftingOrchestrator(Orchestrator):
    """A specialized orchestrator that runs just enough to test the ContractDraftingAgent"""
    
    def __init__(self):
        # Initialize the agents we need
        self.contract_selector_agent = MockIslamicContractSelectorAgent()
        self.contract_drafting_agent = ContractDraftingAgent()
        
        # Define a sequence that includes selection and drafting steps
        self.agent_sequence = [
            (self.contract_selector_agent, "pending_contract_selection"),
            (self.contract_drafting_agent, "pending_contract_formalization")
        ]
        
        # Flag to skip country law validation
        self.run_country_law_validation = False

    def _initialize_pco(self, client_details: dict, project_details: dict) -> dict:
        """Override to set the initial status to pending_contract_selection and add mock data"""
        pco = super()._initialize_pco(client_details, project_details)
        
        # Set status to skip to contract selection
        pco["current_status"] = "pending_contract_selection"
        
        # Get contract type from client_details (added by our test function)
        contract_type = client_details.get("_test_contract_type", "Istisna'a")
        
        # Add a test parameter for contract type
        pco["_test_contract_type"] = contract_type
        
        # Add mock results for previous steps
        pco["enterprise_audit_results"] = {
            "score": 1.75,
            "summary": "The company shows strong financial health with good liquidity and solvency ratios.",
            "key_ratios": {
                "2021": {"Current Ratio": 1.8, "Debt Ratio": 0.4},
                "2022": {"Current Ratio": 2.1, "Debt Ratio": 0.35}
            },
            "risk_level": {"Low": 2, "Moderate": 0, "High": 0},
            "verdict": "APPROVE",
            "warnings": []
        }
        
        pco["project_evaluation_results"] = {
            "is_viable": True,
            "decision": "APPROVE",
            "confidence": 0.85,
            "justification": "The project has a strong business case with reasonable payback period and experienced management.",
            "identified_risks": [
                "Construction timeline risks",
                "Initial cash flow constraints",
                "Regulatory compliance challenges"
            ],
            "shariah_preliminary_fit": f"High compatibility with {contract_type} contract structure"
        }
        
        return pco

    def process_project(self, client_details: dict, project_details: dict) -> dict:
        """Override to extract and save contract drafts when they are generated"""
        pco = self._initialize_pco(client_details, project_details)
        print(f"--- Starting processing for Case ID: {pco['case_id']} ---")

        for agent_instance, required_status in self.agent_sequence:
            if pco["current_status"] == required_status:
                print(f"\n==> Invoking {agent_instance.agent_name} (PCO Status: {pco['current_status']})")
                try:
                    pco = agent_instance.execute(pco)
                    print(f"    Output Status: {pco['current_status']}")
                    
                    # Save contract_draft content (if it exists) for test analysis
                    if agent_instance.agent_name == "ContractDraftingAgent" and "contract_draft" in pco:
                        # Make it accessible for tests
                        pco["test_contract_draft"] = pco["contract_draft"]
                        # Break after drafting (don't continue to next steps)
                        break
                            
                except Exception as e:
                    pco["error_info"] = {
                        "agent": agent_instance.agent_name,
                        "error": str(e),
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    pco["current_status"] = f"error_in_{agent_instance.agent_name.lower().replace(' ','_')}"
                    pco["processing_log"].append({
                        "agent": agent_instance.agent_name,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "status": "error",
                        "error_message": str(e)
                    })
                    print(f"!!! Error during {agent_instance.agent_name} execution: {e} !!!")
                    break # Stop processing on error
            elif pco["current_status"].startswith("error_"):
                print(f"Skipping further processing due to status: {pco['current_status']}")
                break

        print(f"\n--- Processing finished for Case ID: {pco['case_id']}. Final Status: {pco['current_status']} ---")
        return pco

def run_orchestrator_test():
    print("--- Starting ContractDraftingAgent Test via Orchestrator ---")
    
    # Create our specialized orchestrator
    orchestrator = ContractDraftingOrchestrator()
    
    # 1. Test with Istisna'a Contract (Construction Project)
    print("\n=== Test Case 1: Factory Construction Project (Istisna'a) ===")
    client_details_construction = {
        "client_name": "Al-Farabi Manufacturing Group",
        "client_type": "company",
        "experience": "15 years in industrial manufacturing, with 5 successful facility construction projects",
        "_test_contract_type": "Istisna'a"  # Add contract type here
    }
    
    project_details_construction = {
        "project_name": "Advanced Automotive Parts Factory",
        "sector": "Manufacturing / Automotive",
        "location": "Industrial City, Jeddah, Saudi Arabia",
        "estimated_cost": 8500000,
        "expected_revenue": 2300000,
        "payback_period": 5.2,
        "risks": "Construction delays; Equipment installation complexity; Regulatory approvals; Supply chain disruptions; Market competition",
        "objective": "Construct a state-of-the-art manufacturing facility for precision automotive components",
        "description": "This project involves the construction of a 12,000 square meter manufacturing facility with specialized production lines for high-precision automotive components. The facility will include advanced robotics, quality control systems, and environmentally sustainable design elements."
    }
    
    print("Processing Istisna'a contract drafting...")
    result_istisna = orchestrator.process_project(client_details_construction, project_details_construction)
    
    print("\nResults for Istisna'a Contract:")
    print(f"Final Status: {result_istisna['current_status']}")
    
    # Check if contract draft was created
    if "test_contract_draft" in result_istisna:
        print(f"Contract Type: {result_istisna['test_contract_draft']['contract_type']}")
        print(f"Contract Status: {result_istisna['test_contract_draft']['status']}")
        # Show first few lines of contract content
        if result_istisna['test_contract_draft']['content']:
            content_preview = result_istisna['test_contract_draft']['content'].split('\n')[:5]
            print("Content Preview:")
            for line in content_preview:
                print(f"  {line}")
            print("  ...")
    else:
        print("No contract draft was created")
    
    # Save contract draft to file for inspection
    istisna_output_path = os.path.join(OUTPUTS_DIR, 'istisna_contract_output.json')
    with open(istisna_output_path, 'w') as f:
        json.dump(result_istisna, f, indent=2)
    print(f"Full results saved to {istisna_output_path}")
    
    # 2. Test with Murabaha Contract (Equipment Purchase)
    print("\n\n=== Test Case 2: Equipment Financing (Murabaha) ===")
    client_details_equipment = {
        "client_name": "Al-Noor Medical Supplies LLC",
        "client_type": "company",
        "experience": "8 years operating in medical equipment distribution",
        "_test_contract_type": "Murabaha"  # Add contract type here
    }
    
    project_details_equipment = {
        "project_name": "Medical Imaging Equipment Acquisition",
        "sector": "Healthcare",
        "location": "Dubai, UAE",
        "estimated_cost": 3200000,
        "expected_revenue": 950000,
        "payback_period": 3.7,
        "risks": "Technology obsolescence; Maintenance costs; Market demand; Regulatory compliance",
        "objective": "Acquire advanced MRI and CT scanning equipment for leasing to hospitals",
        "description": "This project involves purchasing 2 MRI machines and 3 CT scanners from leading manufacturers for subsequent leasing to major hospitals across the UAE. The equipment will be maintained by Al-Noor's certified technicians."
    }
    
    print("Processing Murabaha contract drafting...")
    result_murabaha = orchestrator.process_project(client_details_equipment, project_details_equipment)
    
    print("\nResults for Murabaha Contract:")
    print(f"Final Status: {result_murabaha['current_status']}")
    
    # Check if contract draft was created
    if "test_contract_draft" in result_murabaha:
        print(f"Contract Type: {result_murabaha['test_contract_draft']['contract_type']}")
        print(f"Contract Status: {result_murabaha['test_contract_draft']['status']}")
        # Show first few lines of contract content
        if result_murabaha['test_contract_draft']['content']:
            content_preview = result_murabaha['test_contract_draft']['content'].split('\n')[:5]
            print("Content Preview:")
            for line in content_preview:
                print(f"  {line}")
            print("  ...")
    else:
        print("No contract draft was created")
    
    # Save contract draft to file for inspection
    murabaha_output_path = os.path.join(OUTPUTS_DIR, 'murabaha_contract_output.json')
    with open(murabaha_output_path, 'w') as f:
        json.dump(result_murabaha, f, indent=2)
    print(f"Full results saved to {murabaha_output_path}")
    
    # 3. Test with Musharakah Contract (Joint Venture)
    print("\n\n=== Test Case 3: Real Estate Development (Musharakah) ===")
    client_details_realestate = {
        "client_name": "Bayt Al-Imar Development Corporation",
        "client_type": "company",
        "experience": "12 years in residential and commercial real estate development with 8 completed projects",
        "_test_contract_type": "Musharakah"  # Add contract type here
    }
    
    project_details_realestate = {
        "project_name": "Al-Waha Mixed-Use Development",
        "sector": "Real Estate",
        "location": "Muscat, Oman",
        "estimated_cost": 15000000,
        "expected_revenue": 4200000,
        "payback_period": 7.5,
        "risks": "Market fluctuations; Construction delays; Regulatory changes; Environmental compliance; Material cost increases",
        "objective": "Develop a 50,000 square meter mixed-use property with residential, retail, and office spaces",
        "description": "This project will create a modern, eco-friendly mixed-use development featuring 120 residential units, 35 retail spaces, and 15,000 square meters of premium office space. The development includes green spaces, smart building technology, and sustainable energy solutions."
    }
    
    print("Processing Musharakah contract drafting...")
    result_musharakah = orchestrator.process_project(client_details_realestate, project_details_realestate)
    
    print("\nResults for Musharakah Contract:")
    print(f"Final Status: {result_musharakah['current_status']}")
    
    # Check if contract draft was created
    if "test_contract_draft" in result_musharakah:
        print(f"Contract Type: {result_musharakah['test_contract_draft']['contract_type']}")
        print(f"Contract Status: {result_musharakah['test_contract_draft']['status']}")
        # Show first few lines of contract content
        if result_musharakah['test_contract_draft']['content']:
            content_preview = result_musharakah['test_contract_draft']['content'].split('\n')[:5]
            print("Content Preview:")
            for line in content_preview:
                print(f"  {line}")
            print("  ...")
    else:
        print("No contract draft was created")
    
    # Save contract draft to file for inspection
    musharakah_output_path = os.path.join(OUTPUTS_DIR, 'musharakah_contract_output.json')
    with open(musharakah_output_path, 'w') as f:
        json.dump(result_musharakah, f, indent=2)
    print(f"Full results saved to {musharakah_output_path}")
    
    print("\n--- Contract Drafting Orchestrator Test Finished ---")

if __name__ == "__main__":
    run_orchestrator_test() 