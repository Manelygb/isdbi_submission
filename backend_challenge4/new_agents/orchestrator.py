import uuid
import datetime
import time

from new_agents.challenge4.base_agent import BaseAgent
from new_agents.challenge4.contract_drafting_agent import ContractDraftingAgent
from new_agents.challenge4.enterprise_audit_agent import EnterpriseAuditAgent
from new_agents.challenge4.project_evaluation_agent import ProjectEvaluationAgent
from new_agents.challenge4.islamic_contract_selector_agent import IslamicContractSelectorAgent
from new_agents.challenge4.accounting_agent import AccountingAgent
from new_agents.challenge4.shariah_compliance_validator_agent import ShariahComplianceValidatorAgent
from new_agents.challenge4.country_laws_validator_agent import CountryLawsValidatorAgent
from new_agents.challenge4.final_decision_agent import FinalDecisionAgent
# from langchain.chains.base import Chain # Example import if agents were actual Chains

# --- 1. Placeholder Agent Classes (Simulating Langchain Agents) ---
# In a real scenario, these would be your Langchain agent implementations.
# They would likely inherit from Langchain's Chain or use AgentExecutor.
# For this example, they just take the PCO, simulate work, and update it.


class Orchestrator:
    def __init__(self, run_country_law_validation=True):
        self.enterprise_audit_agent = EnterpriseAuditAgent()
        self.project_evaluation_agent = ProjectEvaluationAgent()
        self.islamic_contract_selector_agent = IslamicContractSelectorAgent()
        self.accounting_agent = AccountingAgent()
        self.shariah_compliance_validator_agent = ShariahComplianceValidatorAgent()
        self.country_laws_validator_agent = CountryLawsValidatorAgent()
        self.final_decision_agent = FinalDecisionAgent()
        self.contract_drafting_agent = ContractDraftingAgent()
        self.run_country_law_validation = run_country_law_validation

        self.agent_sequence = self._define_agent_sequence()

    def _define_agent_sequence(self):
        # Defines the typical sequence of agents
        sequence = [
            (self.enterprise_audit_agent, "initial"), # done
            (self.project_evaluation_agent, "pending_project_evaluation"), # done
            (self.islamic_contract_selector_agent, "pending_contract_selection"), # done
            (self.contract_drafting_agent, "pending_contract_formalization"), # done
            (self.accounting_agent, "pending_accounting_generation"), # TBD, CH1
            (self.shariah_compliance_validator_agent, "pending_shariah_validation"), # TBD, CH4
        ]
        if self.run_country_law_validation:
            sequence.append((self.country_laws_validator_agent, "pending_country_law_validation")) # done
        
        sequence.append((self.final_decision_agent, "pending_final_decision")) # TBD
        return sequence

    def _initialize_pco(self, client_details: dict, project_details: dict) -> dict:
        return {
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
                "agent": "Orchestrator",
                "timestamp": datetime.datetime.now().isoformat(),
                "message": "PCO initialized.",
                "status": "system"
            }],
            "current_status": "initial", # Starting status
            "error_info": None
        }

    def process_project(self, client_details: dict, project_details: dict) -> dict:
        pco = self._initialize_pco(client_details, project_details)
        print(f"--- Starting processing for Case ID: {pco['case_id']} ---")

        for agent_instance, required_status in self.agent_sequence:
            if pco["current_status"] == required_status:
                print(f"\n==> Invoking {agent_instance.agent_name} (PCO Status: {pco['current_status']})")
                try:
                    pco = agent_instance.execute(pco)
                    print(f"    Output Status: {pco['current_status']}")
                    # Early exit conditions
                    if pco["current_status"] == "project_rejected_evaluation":
                        print(f"!!! Project rejected at evaluation stage. Halting sequence. !!!")
                        # Optionally call final decision agent directly for rejection report
                        pco = self.final_decision_agent.execute(pco)
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
            elif pco["current_status"].startswith("error_") or pco["current_status"] == "project_rejected_evaluation":
                print(f"Skipping further processing due to status: {pco['current_status']}")
                break


        print(f"\n--- Processing finished for Case ID: {pco['case_id']}. Final Status: {pco['current_status']} ---")
        return pco

# --- 3. Example Usage ---
if __name__ == "__main__":
    orchestrator = Orchestrator(run_country_law_validation=True)

    # Example 1: Company client, construction project
    client_data_1 = {
        "client_name": "ABC Manufacturing Co.",
        "client_type": "company",
        "financial_data_csv": """Year,CurrentAssets,CurrentLiabilities,StocksAndRelief,IssuedCapital,TotalLiabilities,TotalAssets,NetIncome,Revenue,NonCurrentAssets,PermanentCapital,FixedAssets
2021,28000,14000,4500,18000,28000,56000,4800,48000,18000,46000,17000
2022,33000,15000,5500,20000,30000,63000,6500,53000,20000,53000,20000
2023,38000,16000,5000,22000,32000,68000,6000,58000,23000,58000,22000"""
    }
    project_data_1 = {
        "project_name": "Custom Factory Construction",
        "description": "Build a custom-built factory for ABC Manufacturing.",
        "estimated_cost": 2000000,
        "duration_months": 12
    }
    
    print("\n\n--- RUNNING EXAMPLE 1 ---")
    final_pco_1 = orchestrator.process_project(client_data_1, project_data_1)
    
    print("\nFinal PCO (Example 1):")
    # For brevity, printing only selected fields. You can print the whole dict.
    print(f"  Case ID: {final_pco_1['case_id']}")
    print(f"  Final Decision: {final_pco_1.get('final_decision_report', {}).get('final_decision')}")
    print(f"  Shariah Compliance: {final_pco_1.get('shariah_compliance_report', {}).get('overall_status')}")
    print(f"  Selected Contract: {final_pco_1.get('selected_contract_details', {}).get('primary_contract_type')}")
    print(f"  Processing Log Length: {len(final_pco_1['processing_log'])}")
    if final_pco_1.get("error_info"):
        print(f"  Error: {final_pco_1['error_info']}")

    # Example 2: Individual client, trade project, skip country law validation
    orchestrator_no_country_law = Orchestrator(run_country_law_validation=False)
    client_data_2 = {
        "client_name": "Mr. Trader Ali",
        "client_type": "individual",
    }
    project_data_2 = {
        "project_name": "Importing Dates for Trade",
        "description": "Importing and selling high-quality dates.",
        "estimated_cost": 50000,
        "duration_months": 3
    }
    print("\n\n--- RUNNING EXAMPLE 2 (No Country Law Validation) ---")
    final_pco_2 = orchestrator_no_country_law.process_project(client_data_2, project_data_2)
    print("\nFinal PCO (Example 2):")
    print(f"  Case ID: {final_pco_2['case_id']}")
    print(f"  Final Decision: {final_pco_2.get('final_decision_report', {}).get('final_decision')}")
    print(f"  Enterprise Audit: {final_pco_2.get('enterprise_audit_results', {}).get('summary')}") # Should be skipped
    print(f"  Country Law Report: {'Present' if final_pco_2.get('country_law_validation_report') else 'Absent'}")

