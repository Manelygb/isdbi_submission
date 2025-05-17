import os
import json
from typing import Dict, List, Optional
from langchain_openai import OpenAIEmbeddings
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from ..custom_chat_models.chat_openrouter import ChatOpenRouter
from .base_agent import BaseAgent

# Load environment variables from .env file
load_dotenv()

MODEL_NAME = "openai/gpt-4o-mini"
EMBEDDING_MODEL_NAME = "text-embedding-3-large"

class ContractSelectionResult(BaseModel):
    """Schema for the structured output of the Islamic contract selection"""
    primary_contract_type: str = Field(
        description="The main Islamic contract type selected (Musharakah, Murabaha, Istisna'a, Ijarah, Salam)",
        examples=["Musharakah", "Murabaha", "Istisna'a", "Ijarah", "Salam"]
    )
    contract_probabilities: Dict[str, float] = Field(
        description="Probability scores for each potential contract type (values should sum to 1.0)",
        examples=[{
            "Musharakah": 0.15, 
            "Murabaha": 0.60, 
            "Istisna'a": 0.10, 
            "Ijarah": 0.10, 
            "Salam": 0.05
        }]
    )
    relevant_aaoifi_fas: List[str] = Field(
        description="List of relevant AAOIFI FAS standards applicable to the primary contract",
        examples=[["FAS 8", "FAS 9"], ["FAS 28"]]
    )
    justification: str = Field(
        description="Detailed explanation of why this contract type is most suitable for the project",
        examples=["Selected Murabaha as the project involves purchase of clearly defined goods with a fixed profit margin."]
    )
    key_parameters_required: List[str] = Field(
        description="List of key parameters required to formalize this contract",
        examples=[["asset_specifications", "cost_price", "profit_margin", "payment_schedule"]]
    )
    supporting_contracts: Optional[List[str]] = Field(
        description="Optional supporting contracts that might be needed alongside the primary contract",
        default=[]
    )

class IslamicContractSelectorAgent(BaseAgent):
    agent_name = "IslamicContractSelectorAgent"

    def __init__(self, vector_store_path="../../vector_storee/index"):
        super().__init__()
        self.embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)
        
        # Adjust path to be relative to this file's location
        script_dir = os.path.dirname(__file__)
        self.db_path = os.path.join(script_dir, vector_store_path)
        
        # Initialize vector store and retriever if available
        try:
            if os.path.exists(self.db_path) and os.path.isdir(self.db_path):
                self.vector_store = FAISS.load_local(self.db_path, self.embeddings, allow_dangerous_deserialization=True)
                self.retriever = self.vector_store.as_retriever()
                self.qa_chain = RetrievalQA.from_chain_type(
                    llm=ChatOpenRouter(model_name=MODEL_NAME),
                    retriever=self.retriever
                )
            else:
                print(f"Warning: FAISS vector store not found at {self.db_path}. Will operate without knowledge retrieval.")
                self.vector_store = None
                self.retriever = None
                self.qa_chain = None
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            self.vector_store = None
            self.retriever = None
            self.qa_chain = None
        
        # Initialize LLM
        self.llm = ChatOpenRouter(model_name=MODEL_NAME, temperature=0.3)
        self.structured_llm = self.llm.with_structured_output(ContractSelectionResult)
        
        print(f"{self.agent_name} initialized.")

    def _perform_task(self, pco: dict):
        pco["processing_log"][-1]["message"] = "Starting Islamic contract selection..."
        
        try:
            # Extract relevant information from PCO
            project_details = pco.get("project_details", {})
            client_details = pco.get("client_details", {})
            enterprise_audit = pco.get("enterprise_audit_results", {})
            project_evaluation = pco.get("project_evaluation_results", {})
            
            if not project_details:
                raise ValueError("Missing project details in PCO")
            
            # Format inputs for the LLM prompt components
            formatted_input = self._format_data(
                project_details=project_details,
                client_details=client_details,
                enterprise_audit=enterprise_audit,
                project_evaluation=project_evaluation
            )
            
            # Generate a prompt string rather than a message list for reliability
            prompt = f"""
You are a specialized Islamic finance expert with deep knowledge of Shariah-compliant contracts and AAOIFI standards.

Your task is to analyze project and client information to select the most appropriate Islamic financial contract for the specific financing situation. You must provide detailed justification for your selection and include probabilities for each potential contract type.

## Key Islamic Financial Contract Types:

1. **Musharakah** (Partnership contract):
   - Appropriate for: Joint ventures, real estate development
   - AAOIFI Standards: FAS 4 & SS 12
   - Key characteristics: Profit-sharing based on agreed ratios, loss-sharing based on capital contribution

2. **Murabaha** (Cost-plus financing):
   - Appropriate for: Trade financing, asset acquisition
   - AAOIFI Standards: FAS 28 & SS 8
   - Key characteristics: Fixed markup, asset must be owned by bank before sale

3. **Istisna'a** (Manufacturing contract):
   - Appropriate for: Construction projects, manufacturing custom assets
   - AAOIFI Standards: FAS 10 & SS 11
   - Key characteristics: Payment can be deferred, specifications agreed upfront

4. **Ijarah** (Lease contract):
   - Appropriate for: Equipment leasing, property rental with option to buy
   - AAOIFI Standards: FAS 32 & SS 9
   - Key characteristics: Bank owns asset, transfers usufruct to client

5. **Salam** (Forward purchase):
   - Appropriate for: Agricultural financing, commodity purchases
   - AAOIFI Standards: FAS 7 & SS 10
   - Key characteristics: Full payment upfront, delivery deferred

I need you to analyze the following information and recommend the most appropriate Islamic finance contract structure:

## Project Information:
{formatted_input.get('project_info', 'No project information available.')}

## Client Information:
{formatted_input.get('client_info', 'No client information available.')}

## Enterprise Audit Results:
{formatted_input.get('audit_info', 'No audit information available.')}

## Project Evaluation Results:
{formatted_input.get('evaluation_info', 'No evaluation information available.')}

Consider all information provided, including project type, financial health, sector, and risks.
"""

            try:
                # Attempt direct model invocation with a clear instruction to format output
                prompt_with_format_instructions = prompt + """

Please respond ONLY with a valid JSON object following EXACTLY this format:

{
  "primary_contract_type": "string - one of: Istisna'a, Musharakah, Murabaha, Ijarah, or Salam",
  "contract_probabilities": {
    "Musharakah": float,
    "Murabaha": float, 
    "Istisna'a": float,
    "Ijarah": float,
    "Salam": float
  },
  "relevant_aaoifi_fas": ["string", "string"],
  "justification": "string",
  "key_parameters_required": ["string", "string"],
  "supporting_contracts": ["string", "string"]
}

Do not include ANY explanatory text, markdown formatting, or code blocks before or after the JSON.
Just return a valid JSON object directly.
"""
                # Use regular LLM instead of structured output
                response = self.llm.invoke(prompt_with_format_instructions)
                
                # Try to extract JSON from the response
                import re
                import json
                
                # First clean up the response
                content = response.content.strip()
                
                # Remove any markdown code block markers
                content = re.sub(r'^```json\s*', '', content)
                content = re.sub(r'^```\s*', '', content)
                content = re.sub(r'\s*```$', '', content)
                
                # Try multiple approaches to extract valid JSON
                try:
                    # Try direct parsing first
                    contract_data = json.loads(content)
                except json.JSONDecodeError:
                    # Try to find JSON object using regex
                    json_match = re.search(r'({[\s\S]*})', content)
                    if json_match:
                        try:
                            json_str = json_match.group(1)
                            contract_data = json.loads(json_str)
                        except json.JSONDecodeError:
                            # If still failing, try to extract just the part that looks most like JSON
                            pattern = r'{\s*"primary_contract_type"[\s\S]*}'
                            json_match = re.search(pattern, content)
                            if json_match:
                                try:
                                    contract_data = json.loads(json_match.group(0))
                                except:
                                    raise ValueError("Could not parse JSON after multiple attempts")
                            else:
                                raise ValueError("Could not extract valid JSON from model response")
                    else:
                        raise ValueError("No JSON-like structure found in response")
                
                # Validate and clean the contract data
                if "primary_contract_type" not in contract_data:
                    raise ValueError("Missing primary_contract_type in response")
                
                # Ensure probabilities add up to 1.0
                if "contract_probabilities" in contract_data:
                    probs = contract_data["contract_probabilities"]
                    total = sum(probs.values())
                    if total > 0 and abs(total - 1.0) > 0.01:  # If not close to 1.0
                        # Normalize probabilities
                        for k in probs:
                            probs[k] = probs[k] / total
                
                # Ensure all required fields are present with sensible defaults if missing
                contract_data.setdefault("contract_probabilities", {
                    "Istisna'a": 0.65, 
                    "Musharakah": 0.20, 
                    "Ijarah": 0.10, 
                    "Murabaha": 0.05, 
                    "Salam": 0.00
                })
                contract_data.setdefault("relevant_aaoifi_fas", ["FAS 10", "SS 11"])
                contract_data.setdefault("justification", f"Selected {contract_data['primary_contract_type']} based on project characteristics.")
                contract_data.setdefault("key_parameters_required", ["asset_specifications", "payment_schedule", "delivery_timeline"])
                contract_data.setdefault("supporting_contracts", [])
                
                # Update PCO with selection results
                pco["selected_contract_details"] = contract_data
            except Exception as inner_e:
                print(f"Error with structured output: {inner_e}. Using fallback selection.")
                pco["selected_contract_details"] = {
                    "primary_contract_type": "Istisna'a",
                    "contract_probabilities": {
                        "Istisna'a": 0.65,
                        "Musharakah": 0.20,
                        "Ijarah": 0.10,
                        "Murabaha": 0.05,
                        "Salam": 0.00
                    },
                    "justification": "Fallback selection based on the construction nature of the project.",
                    "key_parameters_required": ["asset_specifications", "payment_schedule", "delivery_timeline"],
                    "relevant_aaoifi_fas": ["FAS 10", "SS 11"],
                    "supporting_contracts": []
                }
            
            # Update PCO status
            pco["current_status"] = "pending_contract_formalization"
            primary_contract = pco["selected_contract_details"]["primary_contract_type"]
            pco["processing_log"][-1]["message"] = f"Contract type {primary_contract} selected."
            
        except Exception as e:
            error_message = f"Error during Islamic contract selection: {str(e)}"
            pco["selected_contract_details"] = {
                "primary_contract_type": "Error",
                "justification": error_message,
                "key_parameters_required": [],
                "relevant_aaoifi_fas": [],
                "contract_probabilities": {},
                "supporting_contracts": []
            }
            pco["current_status"] = "error_contract_selection"
            pco["processing_log"][-1]["message"] = error_message
            print(f"Critical error in IslamicContractSelectorAgent: {e}")

    def _retrieve_islamic_finance_knowledge(self, project_details: dict) -> str:
        """Retrieve relevant Islamic finance knowledge from vector store"""
        if not self.qa_chain:
            return "No knowledge base available. Using built-in knowledge."
        
        try:
            # Create a good query based on project details
            project_query = f"""
            What are the most suitable Islamic finance contracts for a project with these characteristics:
            - Project name: {project_details.get('project_name', 'Unknown')}
            - Sector: {project_details.get('sector', 'Unknown')}
            - Objective: {project_details.get('objective', 'Unknown')}
            - Estimated cost: ${project_details.get('estimated_cost', 0):,}
            - Expected revenue: ${project_details.get('expected_revenue', 0):,}
            
            Provide details on applicable AAOIFI FAS standards for each potential contract.
            """
            
            # Query the knowledge base
            result = self.qa_chain.invoke(project_query)
            if result and isinstance(result, dict):
                return result.get("result", "No specific knowledge retrieved.")
            return "Unable to retrieve knowledge from vector store."
            
        except Exception as e:
            print(f"Error retrieving knowledge: {e}")
            return "Error retrieving knowledge from the database."

    def _format_data(self, project_details: dict, client_details: dict, 
                    enterprise_audit: dict, project_evaluation: dict) -> dict:
        """Format all input data for the prompt"""
        # Project information
        project_info = f"""
        Project Name: {project_details.get('project_name', 'Untitled')}
        Sector: {project_details.get('sector', 'Unknown')}
        Location: {project_details.get('location', 'Unknown')}
        Estimated Cost: ${project_details.get('estimated_cost', 0):,}
        Expected Annual Revenue: ${project_details.get('expected_revenue', 0):,}
        Payback Period: {project_details.get('payback_period', 0)} years
        Objective: {project_details.get('objective', 'Not specified')}
        Risks: {project_details.get('risks', 'Not specified')}
        """
        
        # Client information
        client_info = f"""
        Client Type: {client_details.get('client_type', 'Unknown')}
        Experience: {client_details.get('experience', 'Unknown')}
        """
        
        # Enterprise audit results
        audit_info = f"""
        Financial Score: {enterprise_audit.get('score', 'N/A')}
        Financial Summary: {enterprise_audit.get('summary', 'N/A')}
        Risk Level: {enterprise_audit.get('risk_level', 'Unknown')}
        """
        
        # Project evaluation results
        evaluation_info = f"""
        Decision: {project_evaluation.get('decision', 'N/A')}
        Confidence: {project_evaluation.get('confidence', 'N/A')}
        Shariah Preliminary Fit: {project_evaluation.get('shariah_preliminary_fit', 'N/A')}
        Identified Risks: {', '.join(project_evaluation.get('identified_risks', ['None']))}
        """
        
        return {
            "project_info": project_info,
            "client_info": client_info,
            "audit_info": audit_info,
            "evaluation_info": evaluation_info
        } 