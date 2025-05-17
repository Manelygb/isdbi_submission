# IMPORTANT: This test script is designed to be run from the project root directory
# (e.g., /mnt/data/hackathons/isdbi/code/) so that the imports work correctly.
# Example: python backend/tests/test_enterprise_audit_agent.py

import sys
import os

# Add the project root directory to Python's path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import json
# Ensure the agent can be imported from its location within the backend package.
from backend.new_agents.challenge4.enterprise_audit_agent import EnterpriseAuditAgent

# python-dotenv is loaded within the agent itself.
# Ensure your .env file (with API keys) is in a discoverable path
# (e.g., project root or current working directory when running this script).

def run_enterprise_audit_agent_test():
    print("--- Starting EnterpriseAuditAgent Test ---")

    # Mock financial data (normally this would come from a database or user input)
    # Read financial data from the mock CSV file
    mock_financials_path = os.path.join(os.path.dirname(__file__), '../data/input/mock_full_financials.csv')
    with open(mock_financials_path, 'r') as f:
        financial_data_csv = f.read()

    # 1. Construct a detailed sample PCO
    sample_pco = {
        "pco_id": "PCO_TEST_ENTERPRISE_001",
        "client_details": {
            "client_name": "Algerian Solar Innovations",
            "client_type": "company",
            "registration_number": "123456789",
            "incorporation_date": "2015-03-17",
            "industry_sector": "Renewable Energy",
            "legal_form": "Limited Company",
            "ownership_structure": {
                "major_shareholders": [
                    {"name": "Ahmed Benali", "ownership_percentage": 45},
                    {"name": "Mariam Kaddour", "ownership_percentage": 30},
                    {"name": "Green Energy Investment Group", "ownership_percentage": 25}
                ]
            },
            "management_team": [
                {"name": "Ahmed Benali", "position": "CEO"},
                {"name": "Fatima Zidane", "position": "CFO"},
                {"name": "Karim Hadj", "position": "CTO"}
            ],
            "contact_information": {
                "primary_address": "123 Avenue de l'Indépendance, Algiers, Algeria",
                "phone": "+213 21 1234567",
                "email": "contact@algsolarinnovations.dz",
                "website": "www.algsolarinnovations.dz"
            },
            "financial_data_csv": financial_data_csv
        },
        "project_details": {
            "project_name": "Development and Operation of a Photovoltaic Solar Park (50MW) in Adrar",
            "project_type": "Renewable Energy - Independent Power Producer (IPP)",
            "location_country": "Algeria",
            "location_specific": "Adrar Region, Wilaya of Adrar",
            "total_project_value_eur": 60000000,
            "financing_sought_eur": 45000000,
            "project_sponsor": {
                "name": "Algerian Renewable Energy Co. (AREC) SPV",
                "type": "Special Purpose Vehicle incorporated in Algeria",
                "shareholders": "Local Investors (60%), International Energy Corp (40%)"
            }
        },
        "processing_log": [
            {"agent_name": "SystemInitializer", "timestamp": "2024-05-22T09:00:00Z", "message": "PCO initiated for Enterprise Audit."}
        ],
        "current_status": "pending_enterprise_audit"
    }

    print(f"Sample PCO ID: {sample_pco['pco_id']}")
    print(f"Client Name: {sample_pco['client_details']['client_name']}")
    print(f"Client Type: {sample_pco['client_details']['client_type']}")
    print(f"Financial Data Preview: {financial_data_csv.split('\\n')[0]}")

    # 2. Instantiate the agent
    agent = None
    try:
        # The EnterpriseAuditAgent's __init__ loads .env and initializes the LLM.
        agent = EnterpriseAuditAgent()
        print(f"Successfully instantiated {agent.agent_name}.")
    except FileNotFoundError as fnf_error:
        print(f"ERROR Instantiating Agent: {fnf_error}")
        print("Ensure the financial data file exists at the expected path.")
        return
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
        print(f"  Timestamp: {log_entry.get('timestamp', 'N/A')}")
        print(f"  Agent: {log_entry.get('agent_name', 'N/A')}")
        print(f"  Message: {log_entry.get('message', 'N/A')}")
        print("-" * 20)

    print("\nEnterprise Audit Results:")
    audit_results = sample_pco.get("enterprise_audit_results")
    if audit_results:
        # Pretty print the JSON report
        print(json.dumps(audit_results, indent=4, ensure_ascii=False))
        
        # Print a more detailed breakdown of key ratios if available
        if "key_ratios" in audit_results and audit_results["key_ratios"]:
            print("\nDetailed Financial Ratios by Year:")
            for year, ratios in audit_results["key_ratios"].items():
                print(f"\nYear: {year}")
                for ratio_name, ratio_value in ratios.items():
                    if ratio_value is not None:
                        print(f"  {ratio_name}: {ratio_value}")
    else:
        print("No audit results were generated in the PCO.")
    
    # 5. Also test with a non-company client to ensure proper handling
    print("\n--- Testing with non-company client ---")
    non_company_pco = sample_pco.copy()
    non_company_pco["client_details"]["client_type"] = "individual"
    non_company_pco["processing_log"] = [
        {"agent_name": "SystemInitializer", "timestamp": "2024-05-22T10:00:00Z", "message": "PCO initiated for Enterprise Audit (Individual)."}
    ]
    
    try:
        agent._perform_task(non_company_pco)
        print(f"Non-company test - PCO Status: {non_company_pco.get('current_status')}")
        print("Non-company test - Audit Results:")
        print(json.dumps(non_company_pco.get("enterprise_audit_results", {}), indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"CRITICAL ERROR during non-company test: {e}")
    
    print("\n--- Test Script Finished ---")
    
    # 6. Test the fallback to mock data (by removing financial_data_csv from PCO)
    print("\n--- Testing fallback to mock data ---")
    fallback_pco = sample_pco.copy()
    # Remove financial_data_csv from client_details
    fallback_pco["client_details"] = {k: v for k, v in fallback_pco["client_details"].items() if k != "financial_data_csv"}
    fallback_pco["processing_log"] = [
        {"agent_name": "SystemInitializer", "timestamp": "2024-05-22T11:00:00Z", "message": "PCO initiated for Enterprise Audit (Fallback)."}
    ]
    
    try:
        agent._perform_task(fallback_pco)
        print(f"Fallback test - PCO Status: {fallback_pco.get('current_status')}")
        print("Fallback test - Did agent use mock data:")
        for log_entry in fallback_pco.get("processing_log", []):
            if "Using mock financial data file" in log_entry.get("message", ""):
                print("  Yes, mock data was used as fallback.")
                break
        else:
            print("  No, mock data was not used.")
    except Exception as e:
        print(f"CRITICAL ERROR during fallback test: {e}")

if __name__ == "__main__":
    run_enterprise_audit_agent_test() 