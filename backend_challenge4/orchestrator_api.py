from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Literal
import json
import os
import datetime
import uuid

from new_agents.orchestrator import Orchestrator
from new_agents.challenge4.enterprise_audit_agent import EnterpriseAuditAgent
from new_agents.challenge4.project_evaluation_agent import ProjectEvaluationAgent
from new_agents.challenge4.islamic_contract_selector_agent import IslamicContractSelectorAgent
from new_agents.challenge4.contract_drafting_agent import ContractDraftingAgent
from new_agents.challenge4.accounting_agent import AccountingAgent
from new_agents.challenge4.shariah_compliance_validator_agent import ShariahComplianceValidatorAgent
from new_agents.challenge4.country_laws_validator_agent import CountryLawsValidatorAgent
from new_agents.challenge4.final_decision_agent import FinalDecisionAgent

app = FastAPI(title="Islamic Banking Orchestrator API")

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path for storing PCO data
PCO_STORAGE_PATH = "data/pco_data"
os.makedirs(PCO_STORAGE_PATH, exist_ok=True)

# Initialize orchestrator
orchestrator = Orchestrator(run_country_law_validation=True)

# Create single instances of each agent
enterprise_audit_agent = EnterpriseAuditAgent()
project_evaluation_agent = ProjectEvaluationAgent()
islamic_contract_selector_agent = IslamicContractSelectorAgent()
contract_drafting_agent = ContractDraftingAgent()
accounting_agent = AccountingAgent()
shariah_compliance_validator_agent = ShariahComplianceValidatorAgent()
country_laws_validator_agent = CountryLawsValidatorAgent()
final_decision_agent = FinalDecisionAgent()

# Models
class ClientDetails(BaseModel):
    client_name: str
    client_type: Literal["company", "individual"]
    financial_data_csv: Optional[str] = None

class ProjectDetails(BaseModel):
    project_name: str
    description: str
    estimated_cost: float
    duration_months: int

class FlowRequest(BaseModel):
    client_details: ClientDetails
    project_details: ProjectDetails

class FlowStatus(BaseModel):
    case_id: str
    current_status: str

# Helper functions
def save_pco(pco: Dict[str, Any]) -> None:
    case_id = pco["case_id"]
    file_path = os.path.join(PCO_STORAGE_PATH, f"{case_id}.json")
    with open(file_path, "w") as f:
        json.dump(pco, f, indent=2)

def load_pco(case_id: str) -> Dict[str, Any]:
    file_path = os.path.join(PCO_STORAGE_PATH, f"{case_id}.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Case ID {case_id} not found")
    
    with open(file_path, "r") as f:
        return json.load(f)

def list_flows() -> List[Dict[str, Any]]:
    files = os.listdir(PCO_STORAGE_PATH)
    flows = []
    
    for file in files:
        if file.endswith(".json"):
            with open(os.path.join(PCO_STORAGE_PATH, file), "r") as f:
                pco = json.load(f)
                flows.append({
                    "case_id": pco["case_id"],
                    "client_name": pco["client_details"]["client_name"],
                    "project_name": pco["project_details"]["project_name"],
                    "current_status": pco["current_status"],
                    "request_timestamp": pco["request_timestamp"]
                })
    
    return flows

# Endpoints
@app.get("/")
def read_root():
    return {"message": "Islamic Banking Orchestrator API is running"}

@app.get("/flows", response_model=List[Dict[str, Any]])
def get_all_flows():
    """Get a list of all flows"""
    return list_flows()

@app.get("/flows/{case_id}", response_model=Dict[str, Any])
def get_flow(case_id: str):
    """Get details of a specific flow by case_id"""
    return load_pco(case_id)

@app.post("/flows/start", response_model=Dict[str, Any])
def start_full_flow(flow_request: FlowRequest):
    """Start a new flow from the beginning"""
    pco = orchestrator.process_project(
        flow_request.client_details.model_dump(),
        flow_request.project_details.model_dump()
    )
    save_pco(pco)
    return pco

@app.post("/flows/{case_id}/next_agent", response_model=Dict[str, Any])
def execute_next_agent(case_id: str):
    """Execute the next agent in the sequence for a given flow"""
    pco = load_pco(case_id)
    
    # Map status to next agent
    status_to_agent = {
        "initial": enterprise_audit_agent,
        "pending_project_evaluation": project_evaluation_agent,
        "pending_contract_selection": islamic_contract_selector_agent,
        "pending_contract_formalization": contract_drafting_agent,
        "pending_accounting_generation": accounting_agent,
        "pending_shariah_validation": shariah_compliance_validator_agent,
        "pending_country_law_validation": country_laws_validator_agent,
        "pending_final_decision": final_decision_agent
    }
    
    current_status = pco["current_status"]
    if current_status not in status_to_agent:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot proceed from current status: {current_status}"
        )
    
    next_agent = status_to_agent[current_status]
    pco = next_agent.execute(pco)
    save_pco(pco)
    return pco

# Individual agent endpoints
@app.post("/agents/enterprise_audit", response_model=Dict[str, Any])
def start_enterprise_audit(pco_data: Dict[str, Any] = Body(...)):
    """Start a flow from the Enterprise Audit agent"""
    # Ensure we have the required fields
    if "client_details" not in pco_data or "project_details" not in pco_data:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields: client_details and project_details"
        )
    
    # Initialize a new PCO if not provided
    if "case_id" not in pco_data:
        pco_data["case_id"] = str(uuid.uuid4())
        pco_data["request_timestamp"] = datetime.datetime.now().isoformat()
        pco_data["processing_log"] = [{
            "agent": "API",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "PCO initialized via API.",
            "status": "system"
        }]
        pco_data["current_status"] = "initial"
    
    pco = enterprise_audit_agent.execute(pco_data)
    save_pco(pco)
    return pco

@app.post("/agents/project_evaluation", response_model=Dict[str, Any])
def start_project_evaluation(pco_data: Dict[str, Any] = Body(...)):
    """Start a flow from the Project Evaluation agent"""
    # Ensure we have the required fields
    if "client_details" not in pco_data or "project_details" not in pco_data:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields: client_details and project_details"
        )
    
    # Initialize enterprise audit results if not present
    if "enterprise_audit_results" not in pco_data:
        pco_data["enterprise_audit_results"] = {
            "status": "manual_entry",
            "summary": "Enterprise audit data manually provided",
            "financial_ratios": {}
        }
    
    # Initialize a new PCO if not provided
    if "case_id" not in pco_data:
        pco_data["case_id"] = str(uuid.uuid4())
        pco_data["request_timestamp"] = datetime.datetime.now().isoformat()
        pco_data["processing_log"] = [{
            "agent": "API",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "PCO initialized via API starting from project evaluation.",
            "status": "system"
        }]
        pco_data["current_status"] = "pending_project_evaluation"
    
    pco = project_evaluation_agent.execute(pco_data)
    save_pco(pco)
    return pco

@app.post("/agents/contract_selection", response_model=Dict[str, Any])
def start_contract_selection(pco_data: Dict[str, Any] = Body(...)):
    """Start a flow from the Islamic Contract Selector agent"""
    # Required data for contract selection
    required_fields = ["client_details", "project_details", "enterprise_audit_results", "project_evaluation_results"]
    for field in required_fields:
        if field not in pco_data:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )
    
    # Initialize a new PCO if not provided
    if "case_id" not in pco_data:
        pco_data["case_id"] = str(uuid.uuid4())
        pco_data["request_timestamp"] = datetime.datetime.now().isoformat()
        pco_data["processing_log"] = [{
            "agent": "API",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "PCO initialized via API starting from contract selection.",
            "status": "system"
        }]
        pco_data["current_status"] = "pending_contract_selection"
    
    pco = islamic_contract_selector_agent.execute(pco_data)
    save_pco(pco)
    return pco

@app.post("/agents/contract_drafting", response_model=Dict[str, Any])
def start_contract_drafting(pco_data: Dict[str, Any] = Body(...)):
    """Start a flow from the Contract Drafting agent"""
    # Required data for contract drafting
    required_fields = ["client_details", "project_details", "selected_contract_details"]
    for field in required_fields:
        if field not in pco_data:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )
    
    # Initialize a new PCO if not provided
    if "case_id" not in pco_data:
        pco_data["case_id"] = str(uuid.uuid4())
        pco_data["request_timestamp"] = datetime.datetime.now().isoformat()
        pco_data["processing_log"] = [{
            "agent": "API",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "PCO initialized via API starting from contract drafting.",
            "status": "system"
        }]
        pco_data["current_status"] = "pending_contract_formalization"
    
    pco = contract_drafting_agent.execute(pco_data)
    save_pco(pco)
    return pco

@app.post("/agents/accounting", response_model=Dict[str, Any])
def start_accounting(pco_data: Dict[str, Any] = Body(...)):
    """Start a flow from the Accounting agent"""
    # Required data for accounting
    required_fields = ["client_details", "project_details", "selected_contract_details", "formalized_contract"]
    for field in required_fields:
        if field not in pco_data:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )
    
    # Initialize a new PCO if not provided
    if "case_id" not in pco_data:
        pco_data["case_id"] = str(uuid.uuid4())
        pco_data["request_timestamp"] = datetime.datetime.now().isoformat()
        pco_data["processing_log"] = [{
            "agent": "API",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "PCO initialized via API starting from accounting.",
            "status": "system"
        }]
        pco_data["current_status"] = "pending_accounting_generation"
    
    pco = accounting_agent.execute(pco_data)
    save_pco(pco)
    return pco

@app.post("/agents/shariah_compliance", response_model=Dict[str, Any])
def start_shariah_compliance(pco_data: Dict[str, Any] = Body(...)):
    """Start a flow from the Shariah Compliance Validator agent"""
    # Required data for shariah compliance
    required_fields = ["client_details", "project_details", "selected_contract_details", 
                      "formalized_contract", "accounting_entries_report"]
    for field in required_fields:
        if field not in pco_data:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )
    
    # Initialize a new PCO if not provided
    if "case_id" not in pco_data:
        pco_data["case_id"] = str(uuid.uuid4())
        pco_data["request_timestamp"] = datetime.datetime.now().isoformat()
        pco_data["processing_log"] = [{
            "agent": "API",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "PCO initialized via API starting from shariah compliance.",
            "status": "system"
        }]
        pco_data["current_status"] = "pending_shariah_validation"
    
    pco = shariah_compliance_validator_agent.execute(pco_data)
    save_pco(pco)
    return pco

@app.post("/agents/country_laws", response_model=Dict[str, Any])
def start_country_laws(pco_data: Dict[str, Any] = Body(...)):
    """Start a flow from the Country Laws Validator agent"""
    # Required data for country laws validation
    required_fields = ["client_details", "project_details", "selected_contract_details", 
                      "formalized_contract", "shariah_compliance_report"]
    for field in required_fields:
        if field not in pco_data:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )
    
    # Initialize a new PCO if not provided
    if "case_id" not in pco_data:
        pco_data["case_id"] = str(uuid.uuid4())
        pco_data["request_timestamp"] = datetime.datetime.now().isoformat()
        pco_data["processing_log"] = [{
            "agent": "API",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "PCO initialized via API starting from country laws validation.",
            "status": "system"
        }]
        pco_data["current_status"] = "pending_country_law_validation"
    
    pco = country_laws_validator_agent.execute(pco_data)
    save_pco(pco)
    return pco

@app.post("/agents/final_decision", response_model=Dict[str, Any])
def start_final_decision(pco_data: Dict[str, Any] = Body(...)):
    """Start a flow from the Final Decision agent"""
    # Required data for final decision
    required_fields = ["client_details", "project_details", "selected_contract_details", 
                      "formalized_contract", "shariah_compliance_report"]
    for field in required_fields:
        if field not in pco_data:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )
    
    # Initialize a new PCO if not provided
    if "case_id" not in pco_data:
        pco_data["case_id"] = str(uuid.uuid4())
        pco_data["request_timestamp"] = datetime.datetime.now().isoformat()
        pco_data["processing_log"] = [{
            "agent": "API",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "PCO initialized via API starting from final decision.",
            "status": "system"
        }]
        pco_data["current_status"] = "pending_final_decision"
    
    pco = final_decision_agent.execute(pco_data)
    save_pco(pco)
    return pco

@app.delete("/flows/{case_id}", response_model=Dict[str, Any])
def delete_flow(case_id: str):
    """Delete a specific flow by case_id"""
    file_path = os.path.join(PCO_STORAGE_PATH, f"{case_id}.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Case ID {case_id} not found")
    
    try:
        os.remove(file_path)
        return {"status": "success", "message": f"Flow with case_id {case_id} has been deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting flow: {str(e)}") 