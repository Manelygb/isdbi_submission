# IMPORTANT: This test script is designed to be run from the project root directory
# (e.g., /mnt/data/hackathons/isdbi/code/) so that the imports work correctly.
# Example: python backend/tests/test_country_laws_agent.py

import sys
import os

# Add the project root directory to Python's path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import json
# Ensure the agent can be imported from its location within the backend package.
from backend.new_agents.challenge4.country_laws_validator_agent import CountryLawsValidatorAgent

# python-dotenv is loaded within the agent itself.
# Ensure your .env file (with OPENAI_API_KEY) is in a discoverable path
# (e.g., project root or current working directory when running this script).

def run_country_laws_validator_test():
    print("--- Starting CountryLawsValidatorAgent Test ---")

    # 1. Construct a detailed sample PCO
    sample_pco = {
        "pco_id": "PCO_TEST_ALGERIA_001",
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
            },
            "key_agreements_anticipated": [
                "Power Purchase Agreement (PPA) with Sonelgaz (national utility)",
                "Land Lease Agreement with local authorities or state land agency",
                "EPC Contract for construction",
                "O&M Contract for operation"
            ],
            "regulatory_framework_notes": "Project falls under Algerian renewable energy feed-in tariff program and laws governing IPPs. Requires specific permits from CREG (Electricity and Gas Regulation Commission).",
            "environmental_and_social_impact": "EIA completed and approved. Land is state-owned, designated for renewable projects.",
            "proposed_collateral_for_financiers": "Pledge over SPV shares, assignment of PPA revenues, mortgage over immovable installations (solar panels, inverters, substation once built), pledge over bank accounts."
        },
        "formalized_contract": """
        This agreement describes a Build, Own, Operate, Transfer (BOOT) project structure, financed through a combination of shareholder equity and a project finance facility structured as a diminishing Musharakah (Partnership) leading to an Ijarah (Lease).

        Parties:
        - Financiers: A consortium of Islamic Banks (Lead Arranger: 'Algerian Islamic Investment Bank').
        - Project Company (Partner/Lessee): Algerian Renewable Energy Co. (AREC) SPV.
        - Key Counterparty: Sonelgaz (as per the Power Purchase Agreement).

        Phase 1: Diminishing Musharakah (Construction & Initial Operation Period - approx. 3 years)
        1.  The Financiers and AREC SPV (representing equity holders) will form a Musharakah (partnership) to fund the development and construction of the 50MW Solar Park.
        2.  Total capital contributions will align with the project budget, with Financiers providing up to EUR 45,000,000 and AREC SPV providing the balance.
        3.  Ownership of the project assets will be proportionate to capital contributions.
        4.  Profits generated from the sale of electricity to Sonelgaz (under the PPA) during this phase will be shared according to a pre-agreed ratio, after deducting operational expenses.
        5.  AREC SPV will manage the project and its operations.
        6.  The Financiers' share in the Musharakah will be gradually bought out by AREC SPV over an agreed period using a portion of the project's net revenues, effectively diminishing the Financiers' equity stake.

        Phase 2: Ijarah (Lease - Post Musharakah Buy-Out or for specific assets)
        1.  Contingent upon full buyout of the Musharakah shares, or for specific major equipment from the outset, an Ijarah structure may be implemented.
        2.  Alternatively, if the primary structure remains Diminishing Musharakah until full SPV ownership, this Ijarah section may apply to refinancing or expansion.
        3.  For this example, assume the primary path is Diminishing Musharakah where AREC SPV eventually owns 100% of the assets.
        4.  The terms of asset transfer (BOOT model) to the state (likely Sonelgaz or another state entity) after the concession period (e.g., 25 years) must be clearly defined and compliant with Algerian PPP and concession laws.

        Legal & Regulatory Considerations for Algeria:
        - The PPA with Sonelgaz must be validated and adhere to Algerian public procurement and energy sector regulations.
        - Foreign ownership percentage in the SPV and rules for profit repatriation for the international shareholder need to comply with Algerian foreign investment laws.
        - Land lease terms must be compatible with Algerian property law and state land management policies.
        - All contracts must be registered as required by Algerian law. Tax implications (VAT, corporate income tax on SPV, withholding taxes on profit distributions or international payments) must be structured optimally and compliantly.
        - Enforceability of collateral (especially assignment of PPA rights) and step-in rights for lenders under Algerian law is critical.
        - The overall structure must not contravene Algerian civil code, commercial code, or any specific financial regulations.
        """,
        "processing_log": [
            {"agent_name": "SystemInitializer", "timestamp": "2024-05-22T09:00:00Z", "message": "PCO initiated for Country Law Validation."}
        ],
        "current_status": "pending_country_law_validation"
    }

    print(f"Sample PCO ID: {sample_pco['pco_id']}")
    print(f"Project Name: {sample_pco['project_details']['project_name']}")
    print(f"Contract Type Hint: {sample_pco['formalized_contract'][:100]}...") # First 100 chars

    # 2. Instantiate the agent
    agent = None
    try:
        # The CountryLawsValidatorAgent's __init__ loads .env, embeddings, FAISS.
        # Its internal vector_store_path is relative to the agent's own file location.
        agent = CountryLawsValidatorAgent()
        print(f"Successfully instantiated {agent.agent_name}.")
    except FileNotFoundError as fnf_error:
        print(f"ERROR Instantiating Agent: {fnf_error}")
        print("Ensure the FAISS vector store exists at the expected path (the agent calculates this as relative to its own file: backend/new_agents/challenge4/../../vector_storee/law_docs).")
        return
    except ValueError as val_error: # For OPENAI_API_KEY missing
        print(f"ERROR Instantiating Agent: {val_error}")
        print("Ensure OPENAI_API_KEY is set in your .env file (accessible from the project root).")
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
        print(f"  Timestamp: {log_entry.get('timestamp')}")
        print(f"  Agent: {log_entry.get('agent_name')}")
        print(f"  Message: {log_entry.get('message')}")
        print("-" * 20)

    print("\nCountry Law Validation Report:")
    validation_report = sample_pco.get("country_law_validation_report")
    if validation_report:
        # Pretty print the JSON report
        print(json.dumps(validation_report, indent=4, ensure_ascii=False))
    else:
        print("No validation report was generated in the PCO.")
    
    print("\n--- Test Script Finished ---")

if __name__ == "__main__":
    run_country_laws_validator_test() 