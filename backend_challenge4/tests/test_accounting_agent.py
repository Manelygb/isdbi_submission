# IMPORTANT: This test script is designed to be run from the project root directory
# (e.g., /mnt/data/hackathons/isdbi/code/) so that the imports work correctly.
# Example: python backend/tests/test_accounting_agent.py

import sys
import os
import datetime
import json

# Add the project root directory to Python's path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Ensure the agent can be imported from its location within the backend package.
from backend.new_agents.challenge4.accounting_agent import AccountingAgent
from backend.new_agents.challenge4.base_agent import BaseAgent

# Ensure outputs directory exists
OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), 'outputs')
os.makedirs(OUTPUTS_DIR, exist_ok=True)

class MockContractDraftingAgent(BaseAgent):
    """Mock agent to simulate contract drafting step"""
    agent_name = "MockContractDraftingAgent"

    def _perform_task(self, pco: dict):
        contract_type = pco.get("selected_contract_details", {}).get("primary_contract_type", "Istisna'a")
        
        # A simplified contract draft based on the contract type
        contract_content = self._get_mock_contract_content(contract_type)
        
        pco["contract_draft"] = {
            "content": contract_content,
            "contract_type": contract_type,
            "version": "1.0",
            "status": "draft_completed"
        }
        
        pco["current_status"] = "pending_accounting_generation"
        pco["processing_log"][-1]["message"] = f"Contract draft completed for {contract_type} contract."
    
    def _get_mock_contract_content(self, contract_type):
        """Get mock contract content based on contract type"""
        if contract_type == "Istisna'a":
            return """
# ISLAMIC FINANCING SCENARIO: ISTISNA'A

## CONTRACT OVERVIEW
This Istisna'a (manufacturing contract) structure will finance the construction of a custom-built factory for ABC Manufacturing Co. The bank will commission the construction and then deliver the completed facility to the client against deferred payments.

## CONTRACT STRUCTURE
- **Contract Type:** Istisna'a with Parallel Istisna'a
- **Parties:** XYZ Islamic Bank (Financier), ABC Manufacturing Co. (End Buyer), BuildWell Ltd. (Contractor)
- **Subject Matter:** Custom-built manufacturing facility with specified technical requirements
- **Timeline:** 12-month construction period, followed by 4-year payment period

## FINANCIAL STRUCTURE
- **Total Financing Amount:** $2,000,000
- **Payment Mechanism:** 4 quarterly installments of $500,000 starting 3 months after delivery
- **Profit/Return Structure:** Bank earns $300,000 (difference between Istisna'a price to client and Parallel Istisna'a cost)
- **Risk Distribution:** Bank bears construction risk until delivery; client bears payment obligation risk
"""
        elif contract_type == "Murabaha":
            return """
# ISLAMIC FINANCING SCENARIO: MURABAHA

## CONTRACT OVERVIEW
This Murabaha (cost-plus financing) structure will finance the purchase of manufacturing equipment for XYZ Corporation. The bank will purchase the equipment outright and then sell it to the client at a marked-up price with deferred payment terms.

## CONTRACT STRUCTURE
- **Contract Type:** Commodity Murabaha
- **Parties:** ABC Islamic Bank (Seller), XYZ Corporation (Buyer), Equipment Supplier (Original Seller)
- **Subject Matter:** Industrial manufacturing equipment as specifically identified in appendix
- **Timeline:** Immediate purchase and transfer of ownership, with 36-month repayment period

## FINANCIAL STRUCTURE
- **Total Financing Amount:** $500,000 (Cost Price) + $75,000 (Profit) = $575,000 (Murabaha Price)
- **Payment Mechanism:** 36 equal monthly installments of $15,972.22
- **Profit/Return Structure:** Fixed profit amount of $75,000 (15% of Cost Price) disclosed upfront
- **Risk Distribution:** Bank bears ownership risk until sale to client; client bears credit risk after purchase
"""
        elif contract_type == "Ijarah":
            return """
# ISLAMIC FINANCING SCENARIO: IJARAH

## CONTRACT OVERVIEW
This Ijarah Muntahia Bittamleek (lease ending with ownership) structure will finance office space for ABC Company. The bank will purchase the property and lease it to the client, with ownership transferring at the end of the lease term.

## CONTRACT STRUCTURE
- **Contract Type:** Ijarah Muntahia Bittamleek
- **Parties:** XYZ Islamic Bank (Lessor), ABC Company (Lessee)
- **Subject Matter:** Commercial office space in downtown business district
- **Timeline:** 5-year lease period with ownership transfer at the end

## FINANCIAL STRUCTURE
- **Total Asset Cost:** $1,000,000
- **Monthly Rental:** $20,000
- **Total Lease Amount:** $1,200,000 (60 months × $20,000)
- **Profit Component:** $200,000 (Total Lease Amount - Asset Cost)
- **Transfer Mechanism:** Gift (Hibah) at end of lease term if all payments are made
"""
        elif contract_type == "Musharakah":
            return """
# ISLAMIC FINANCING SCENARIO: MUSHARAKAH

## CONTRACT OVERVIEW
This Diminishing Musharakah (partnership) structure will finance a commercial real estate development project. The bank and client will jointly own the project, with the client gradually buying out the bank's share.

## CONTRACT STRUCTURE
- **Contract Type:** Diminishing Musharakah
- **Parties:** XYZ Islamic Bank (Partner), ABC Development Co. (Partner/Manager)
- **Subject Matter:** Mixed-use commercial development project
- **Timeline:** 10-year partnership with gradual buyout

## FINANCIAL STRUCTURE
- **Total Project Cost:** $10,000,000
- **Bank Contribution:** $7,000,000 (70% initial ownership)
- **Client Contribution:** $3,000,000 (30% initial ownership)
- **Profit Sharing Ratio:** 60:40 (Bank:Client)
- **Annual Bank Share Buyout:** $700,000
- **Rental Rate:** 8% per annum on outstanding bank share
"""
        elif contract_type == "Salam":
            return """
# ISLAMIC FINANCING SCENARIO: SALAM

## CONTRACT OVERVIEW
This Salam (forward purchase) contract will finance agricultural production by providing upfront payment for future delivery of crops. The bank pays the full amount to the farmer at contract signing, with specified crop delivery at a future date.

## CONTRACT STRUCTURE
- **Contract Type:** Salam with Parallel Salam
- **Parties:** XYZ Islamic Bank (Buyer), ABC Farms (Seller), Agricultural Trading Co. (End Buyer in Parallel Salam)
- **Subject Matter:** 1,000 tons of wheat with specified quality specifications
- **Timeline:** Payment now, delivery in 6 months

## FINANCIAL STRUCTURE
- **Salam Purchase Price:** $400,000 (paid upfront to farmer)
- **Parallel Salam Selling Price:** $440,000 (to be received from end buyer upon delivery)
- **Bank's Margin:** $40,000 (10% of purchase price)
- **Risk Mitigation:** Bank requires security deposit from farmer
"""
        else:
            return f"""
# ISLAMIC FINANCING SCENARIO: {contract_type.upper()}

## CONTRACT OVERVIEW
This is a generic contract overview for testing the {contract_type} contract type.

## CONTRACT STRUCTURE
- **Contract Type:** {contract_type}
- **Parties:** XYZ Islamic Bank (Financier), ABC Company (Client)
- **Subject Matter:** Project assets
- **Timeline:** 5-year term

## FINANCIAL STRUCTURE
- **Total Financing Amount:** $1,000,000
- **Payment Schedule:** Quarterly payments
- **Profit/Return Structure:** Profit rate of 5% per annum
- **Risk Distribution:** Shared between bank and client
"""


def create_test_pco(contract_type):
    """Create a test PCO with the specified contract type"""
    return {
        "case_id": f"TEST_{contract_type.upper()}_001",
        "request_timestamp": datetime.datetime.now().isoformat(),
        "client_details": {
            "client_name": "ABC Test Company",
            "client_type": "company",
            "experience": "10 years in industry"
        },
        "project_details": {
            "project_name": f"Test {contract_type} Project",
            "objective": f"Test the accounting treatment for {contract_type} contract",
            "estimated_cost": 1000000,
            "expected_revenue": 1200000,
            "sector": "Manufacturing"
        },
        "selected_contract_details": {
            "primary_contract_type": contract_type,
            "justification": f"Selected {contract_type} as it suits the project nature.",
            "key_parameters_required": ["price", "delivery_schedule", "specifications"],
            "relevant_aaoifi_fas": ["Relevant FAS Standard"]
        },
        "processing_log": [{
            "agent": "TestInitializer",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "Test PCO initialized.",
            "status": "system"
        }],
        "current_status": "pending_contract_formalization"
    }

def run_accounting_agent_test():
    print("--- Starting AccountingAgent Test ---")

    # Contract types to test
    contract_types = ["Istisna'a", "Murabaha", "Ijarah", "Musharakah", "Salam"]
    
    for contract_type in contract_types:
        print(f"\n=== Testing AccountingAgent with {contract_type} Contract ===")
        
        # 1. Create test PCO
        test_pco = create_test_pco(contract_type)
        print(f"Created Test PCO with ID: {test_pco['case_id']}")
        
        # 2. Mock the contract drafting step
        mock_drafter = MockContractDraftingAgent()
        mock_drafter.execute(test_pco)
        print(f"Contract draft created with status: {test_pco['current_status']}")
        
        # 3. Instantiate the accounting agent
        agent = None
        try:
            agent = AccountingAgent()
            print(f"Successfully instantiated {agent.agent_name}.")
        except Exception as e:
            print(f"Error instantiating AccountingAgent: {e}")
            continue
        
        # 4. Process the PCO with the accounting agent
        if agent:
            try:
                test_pco = agent.execute(test_pco)
                print(f"Accounting entries generated. New status: {test_pco['current_status']}")
                
                # Save results to file
                result_filename = f"{contract_type.lower().replace('\'', '')}_accounting_output.json"
                output_path = os.path.join(OUTPUTS_DIR, result_filename)
                with open(output_path, 'w') as f:
                    json.dump(test_pco, f, indent=2)
                print(f"Results saved to {output_path}")
                
                # Display accounting entries preview
                accounting_report = test_pco.get("accounting_entries_report", {})
                if accounting_report.get("status") == "completed":
                    content = accounting_report.get("content", "")
                    if content:
                        preview_lines = content.split('\n')[:10]
                        print("\nAccounting Entries Preview:")
                        for line in preview_lines:
                            print(f"  {line}")
                        print("  ...")
                    else:
                        print("\nAccounting Entries Content is empty")
                else:
                    print(f"\nAccounting Entries Generation Status: {accounting_report.get('status', 'unknown')}")
                    if accounting_report.get("error"):
                        print(f"Error: {accounting_report.get('error')}")
                
            except Exception as e:
                print(f"Error executing AccountingAgent: {e}")
                
                # Save error results
                error_filename = f"{contract_type.lower().replace('\'', '')}_accounting_error.json"
                error_path = os.path.join(OUTPUTS_DIR, error_filename)
                with open(error_path, 'w') as f:
                    json.dump(test_pco, f, indent=2)
                print(f"Error details saved to {error_path}")

    print("\n--- AccountingAgent Test Completed ---")

if __name__ == "__main__":
    run_accounting_agent_test() 