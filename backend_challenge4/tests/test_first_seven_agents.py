import os
import sys
import json
import uuid
import datetime
import pandas as pd
from pathlib import Path


# Add the parent directory to sys.path to import backend modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))  # Get to the root directory 
sys.path.insert(0, project_root)  # Add project root to path

from backend.new_agents.challenge4.enterprise_audit_agent import EnterpriseAuditAgent
from backend.new_agents.challenge4.project_evaluation_agent import ProjectEvaluationAgent
from backend.new_agents.challenge4.islamic_contract_selector_agent import IslamicContractSelectorAgent
from backend.new_agents.challenge4.contract_drafting_agent import ContractDraftingAgent
from backend.new_agents.challenge4.final_decision_agent import FinalDecisionAgent
from backend.new_agents.challenge4.accounting_agent import AccountingAgent
from backend.new_agents.challenge4.shariah_compliance_validator_agent import ShariahComplianceValidatorAgent
from backend.new_agents.challenge4.country_laws_validator_agent import CountryLawsValidatorAgent

def load_financial_data():
    """Load financial data from bilan_new.csv"""
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           'data', 'input', 'bilan_new.csv')
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Financial data file not found at {csv_path}")
    
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Create a more complete mapping of columns
    column_mapping = {
        'year': 'Year',
        'non_current_assets': 'NonCurrentAssets',
        'current_assets': 'CurrentAssets', 
        'short_term_debt': 'CurrentLiabilities',  # Using short-term debt as current liabilities
        'total_assets': 'TotalAssets',
        'issued_capital': 'IssuedCapital',
        'total_liabilities': 'TotalLiabilities',
        'net_income': 'NetIncome',
        'stocks': 'StocksAndRelief',
        'revenue': 'Revenue',
        'tangible_assets': 'FixedAssets',
    }
    
    # Apply column renaming for the fields the agent uses
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df[new_col] = df[old_col]
    
    # Calculate missing fields if needed
    if 'CurrentLiabilities' not in df.columns and 'short_term_debt' in df.columns:
        df['CurrentLiabilities'] = df['short_term_debt'] + df['supplier_debt']
    
    # Calculate PermanentCapital if needed
    if 'IssuedCapital' in df.columns and 'TotalLiabilities' in df.columns:
        df['PermanentCapital'] = df['IssuedCapital'] + df['TotalLiabilities']
    
    # Convert to CSV string for the agent
    financial_data_csv = df.to_csv(index=False)
    
    return financial_data_csv

def create_pco():
    """Create a Process Control Object (PCO) with client details and project details"""
    financial_data_csv = load_financial_data()
    
    # Client details for a company
    client_details = {
        "client_name": "Algerian Development Corporation",
        "client_type": "company",
        "financial_data_csv": financial_data_csv,
        "experience": "10 years in real estate and infrastructure development",
        "industry": "Construction and Development"
    }
    
    # Project details for a viable project idea
    # Creating a sustainable infrastructure project which is a good fit for Islamic financing
    project_details = {
        "project_name": "Green Energy Industrial Park",
        "description": "Development of an industrial park with integrated renewable energy systems",
        "sector": "Infrastructure",
        "location": "Algiers, Algeria",
        "estimated_cost": 25000000,
        "expected_revenue": 8500000,  # Increased revenue for better revenue-to-cost ratio (0.34)
        "payback_period": 6,  # Reduced payback period for better viability
        "duration_months": 30,  # Reduced duration
        "objective": "Create a state-of-the-art industrial park with solar power generation, smart grid systems, and sustainable water management",
        "risks": "Construction delays; regulatory approvals",  # Reduced number of risks
        "social_impact": "Job creation for approximately 2,000 people; reducing carbon emissions by 30,000 tons annually",
        "environmental_considerations": "Solar power generation; water recycling; energy-efficient buildings"
    }
    
    # Initialize PCO
    pco = {
        "case_id": str(uuid.uuid4()),
        "request_timestamp": datetime.datetime.now().isoformat(),
        "client_details": client_details,
        "project_details": project_details,
        "enterprise_audit_results": None,
        "project_evaluation_results": None,
        "selected_contract_details": None,
        "formalized_contract": None,
        "accounting_entries_report": None,
        "shariah_compliance_report": None,
        "country_law_validation_report": None,
        "final_decision_report": None,
        "processing_log": [{
            "agent": "Test Script",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "PCO initialized for testing seven agents.",
            "status": "system"
        }],
        "current_status": "initial",
        "error_info": None
    }
    
    return pco

def save_pco_output(pco, filename=None):
    """Save PCO to a JSON file in the outputs directory"""
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"first_seven_agents_test_{timestamp}.json"
    
    # Ensure the outputs directory exists
    outputs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)
    
    # Save PCO as JSON
    output_path = os.path.join(outputs_dir, filename)
    
    # Convert datetime objects to strings
    pco_serializable = json.loads(json.dumps(pco, default=str))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(pco_serializable, f, indent=2, ensure_ascii=False)
    
    print(f"PCO saved to {output_path}")
    return output_path

def run_first_seven_agents():
    """Run the first 7 agents in sequence"""
    # Create initial PCO
    pco = create_pco()
    print(f"--- Starting test with Case ID: {pco['case_id']} ---")
    
    # Initialize agents
    agents = [
        EnterpriseAuditAgent(),
        ProjectEvaluationAgent(),
        IslamicContractSelectorAgent(),
        ContractDraftingAgent(),
        AccountingAgent(),
        ShariahComplianceValidatorAgent(),
        CountryLawsValidatorAgent(),
        FinalDecisionAgent()
    ]
    
    # Run each agent in sequence
    for agent in agents:
        print(f"\n==> Running {agent.agent_name}")
        try:
            pco = agent.execute(pco)
            print(f"    Status after execution: {pco['current_status']}")
            
            # Check for errors or rejection
            if pco["current_status"].startswith("error_"):
                print(f"!!! Error encountered: {pco['current_status']} !!!")
                break
            elif pco["current_status"] == "project_rejected_evaluation":
                print(f"!!! Project rejected at evaluation stage !!!")
                break
                
        except Exception as e:
            print(f"!!! Exception during {agent.agent_name} execution: {e} !!!")
            pco["error_info"] = {
                "agent": agent.agent_name,
                "error": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
            pco["current_status"] = f"error_in_{agent.agent_name.lower().replace(' ','_')}"
            break
    
    # Save the final PCO
    output_path = save_pco_output(pco)
    
    # Print summary
    print("\n--- Final Status Summary ---")
    print(f"Final status: {pco['current_status']}")
    
    if pco.get("enterprise_audit_results"):
        print(f"Enterprise Audit Score: {pco['enterprise_audit_results'].get('score')}")
    
    if pco.get("project_evaluation_results"):
        print(f"Project Evaluation: {pco['project_evaluation_results'].get('decision')}")
    
    if pco.get("selected_contract_details"):
        print(f"Selected Contract: {pco['selected_contract_details'].get('primary_contract_type')}")
    
    if pco.get("formalized_contract"):
        contract_length = len(str(pco['formalized_contract'].get('document_text', '')))
        print(f"Formalized Contract: {contract_length} characters")
    
    if pco.get("accounting_entries_report"):
        entries_length = len(str(pco['accounting_entries_report'].get('content', '')))
        print(f"Accounting Entries: {entries_length} characters")
        
        # Print a preview of accounting entries if they exist
        if entries_length > 0:
            content = pco['accounting_entries_report'].get('content', '')
            preview_lines = content.split('\n')[:5]
            print("\nAccounting Entries Preview:")
            for line in preview_lines:
                print(f"  {line}")
            print("  ...")
            
    if pco.get("shariah_compliance_report"):
        print(f"Shariah Compliance: {pco['shariah_compliance_report'].get('status')}")
        print(f"Overall Status: {pco['shariah_compliance_report'].get('overall_status')}")
        
        # Print issues if any
        issues = pco['shariah_compliance_report'].get('issues', [])
        if issues:
            print(f"  Issues found: {len(issues)}")
            
    if pco.get("country_law_validation_report"):
        print(f"Country Law Validation: {pco['country_law_validation_report'].get('status')}")
        print(f"Is Compliant: {pco['country_law_validation_report'].get('is_compliant')}")
        
        # Print issues if any
        issues = pco['country_law_validation_report'].get('issues_or_risks', [])
        if issues:
            print(f"  Legal issues/risks found: {len(issues)}")
    
    if pco.get("final_decision_report"):
        print(f"Final Decision: {pco['final_decision_report'].get('decision')}")
        print(f"Decision Reason: {pco['final_decision_report'].get('reasoning')}")
    
    return pco, output_path

if __name__ == "__main__":
    pco, output_path = run_first_seven_agents()
    print(f"\nTest completed. Output saved to: {output_path}") 