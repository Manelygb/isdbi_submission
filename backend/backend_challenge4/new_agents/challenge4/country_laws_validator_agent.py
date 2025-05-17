import os
import json
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from ..custom_chat_models.chat_openrouter import ChatOpenRouter
from .base_agent import BaseAgent
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal

# Load environment variables from .env file
load_dotenv()

MODEL_NAME = "google/gemini-2.0-flash-001"
# MODEL_NAME = "openai/gpt-4o"
EMBEDDING_MODEL_NAME = "BAAI/bge-base-en-v1.5"

class ValidationResult(BaseModel):
    is_compliant: bool = Field(description="Whether the contract is compliant with Algerian law")
    issues_or_risks: List[str] = Field(description="List of specific legal issues or risks. Empty list if none.")
    notes_or_observations: List[str] = Field(description="Justifications for compliance/non-compliance, or other relevant observations")
    confidence_score: float = Field(description="Confidence score between 0.0 and 1.0")

class CountryLawsValidatorAgent(BaseAgent):
    agent_name = "CountryLawsValidatorAgent"

    def __init__(self, vector_store_path="../../vector_storee/law_docs_hf"): # Adjusted path and added model_name parameter
        super().__init__()
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

        
        # Adjust path to be relative to this file's location if necessary
        # Assuming this script is in backend/new_agents/challenge4/
        # and vector store is in backend/vector_storee/law_docs
        # The path should be relative from the script's CWD when it runs,
        # or an absolute path. For simplicity, this assumes script is run from a CWD where this relative path is valid.
        # A more robust solution might involve calculating absolute paths.
        script_dir = os.path.dirname(__file__)
        self.db_path = os.path.join(script_dir, vector_store_path)
        
        if not os.path.exists(self.db_path) or not os.path.isdir(self.db_path):
            raise FileNotFoundError(f"FAISS vector store not found at {self.db_path}. Please ensure it's built and path is correct.")
            
        self.vector_store = FAISS.load_local(self.db_path, self.embeddings, allow_dangerous_deserialization=True)
        
        # Replace ChatOpenAI with ChatOpenRouter and use with_structured_output
        self.llm = ChatOpenRouter(model_name=MODEL_NAME)
        self.structured_llm = self.llm.with_structured_output(ValidationResult)
        
        print(f"{self.agent_name} initialized. FAISS store loaded from {self.db_path}")

    def _perform_task(self, pco: dict):
        pco["processing_log"][-1]["message"] = "Starting country law validation..."
        
        project_details = pco.get("project_details")
        formalized_contract = pco.get("formalized_contract")

        if not project_details:
            pco["country_law_validation_report"] = {
                "status": "error",
                "is_compliant": False,
                "issues_or_risks": ["Missing project details in PCO."],
                "notes_or_observations": [],
                "confidence_score": 0.0,
                "remarks": "Cannot perform validation due to missing input.",
                "country_profile": "Algeria (target)"
            }
            pco["current_status"] = "error_country_law_validation"
            pco["processing_log"][-1]["message"] = "Error: Missing project_details."
            return

        # Handle formalized_contract in various formats
        contract_text = ""
        if not formalized_contract:
            # Try to get from contract_draft if formalized_contract not available
            contract_draft = pco.get("contract_draft")
            if contract_draft:
                if isinstance(contract_draft, dict) and "content" in contract_draft:
                    contract_text = contract_draft.get("content", "")
                elif isinstance(contract_draft, str):
                    contract_text = contract_draft
                else:
                    contract_text = str(contract_draft)
            
            if not contract_text:
                pco["country_law_validation_report"] = {
                    "status": "error",
                    "is_compliant": False,
                    "issues_or_risks": ["Missing formalized contract in PCO."],
                    "notes_or_observations": [],
                    "confidence_score": 0.0,
                    "remarks": "Cannot perform validation due to missing contract.",
                    "country_profile": "Algeria (target)"
                }
                pco["current_status"] = "error_country_law_validation"
                pco["processing_log"][-1]["message"] = "Error: Missing formalized_contract or contract_draft."
                return
        else:
            # Extract text from formalized_contract
            if isinstance(formalized_contract, dict) and "document_text_summary" in formalized_contract:
                contract_text = formalized_contract.get("document_text_summary", "")
            elif isinstance(formalized_contract, str):
                contract_text = formalized_contract
            else:
                contract_text = str(formalized_contract)

        # Combine project details and contract for a comprehensive query
        query_text = f"Project Details: {json.dumps(project_details, indent=2)}\n\nFormalized Contract: {contract_text}"
        
        try:
            # Retrieve relevant documents using RAG
            retrieved_docs = self.vector_store.similarity_search(query_text, k=5)
            print("retrieved_docs: ", retrieved_docs)
            legal_context = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
            if not retrieved_docs:
                legal_context = "No specific legal context retrieved. Proceeding with general knowledge."
                pco["processing_log"][-1]["message"] += " Warning: No specific documents retrieved from vector store."

            prompt = self._build_prompt(contract_text, project_details, legal_context)
            
            # Use structured output to enforce the schema
            validation_result = self.structured_llm.invoke(prompt)
            
            # The response is already properly structured as a ValidationResult object
            pco["country_law_validation_report"] = {
                "status": "completed",
                "is_compliant": validation_result.is_compliant,
                "issues_or_risks": validation_result.issues_or_risks,
                "notes_or_observations": validation_result.notes_or_observations,
                "confidence_score": validation_result.confidence_score,
                "retrieved_context_summary": f"Retrieved {len(retrieved_docs)} context snippets.",
                "country_profile": "Algeria (analyzed)" 
            }
            pco["current_status"] = "pending_final_decision"
            pco["processing_log"][-1]["message"] = "Country law validation completed successfully."

        except Exception as e:
            error_message = f"Error during country law validation: {str(e)}"
            pco["country_law_validation_report"] = {
                "status": "error",
                "is_compliant": False,
                "issues_or_risks": [error_message],
                "notes_or_observations": [],
                "confidence_score": 0.0,
                "remarks": "An unexpected error occurred during validation.",
                "country_profile": "Algeria (target)"
            }
            pco["current_status"] = "error_country_law_validation"
            pco["processing_log"][-1]["message"] = error_message
            # Re-raise the exception if you want the agent runner to catch it,
            # or handle it gracefully here. For now, logging and setting error status.
            print(f"Critical error in CountryLawsValidatorAgent: {e}")


    def _build_prompt(self, contract_details_string: str, project_details_object: dict, retrieved_legal_documents_string: str) -> str:
        project_details_str = json.dumps(project_details_object, indent=2, ensure_ascii=False)

        return f"""You are a meticulous legal reasoning agent specializing in Algerian national law and its application to Islamic finance contracts.
Your task is to evaluate whether the provided Islamic finance contract and its underlying project are compliant with Algerian law.

**Country of Operation:** Algeria

**Input Data:**

1.  **Formalized Contract (Natural Language Description of Islamic Financial Structure):**
    ```text
    {contract_details_string}
    ```

2.  **Project Details (Financial, Operational, Structural Information):**
    ```json
    {project_details_str}
    ```

3.  **Retrieved Algerian Legal Context (for reference, from translated legal documents):**
    ```text
    {retrieved_legal_documents_string}
    ```

**Analysis Required:**

Carefully review all provided information: the contract terms (e.g., payment schedule, asset transfer, ownership rights, profit/loss sharing, collateral) and the project details. 
Compare these against the retrieved Algerian legal context and your general knowledge of Algerian commercial, financial, and civil law.
Your analysis must focus on secular legal enforceability and validity within Algeria.

Identify any potential violations, unenforceability, non-compliance, grey areas, or red flags. Examples include, but are not limited to:
- Illegality or unenforceability of deferred ownership structures.
- Restrictions or specific regulations on private leasing or Ijarah contracts.
- Unaddressed or improperly handled tax liabilities (e.g., VAT, stamp duties, corporate tax on SPVs).
- Requirements for banking or financial institution licenses for certain financing activities.
- Conflicts with Algerian contract law, property law, or company law.
- Issues related to collateral, guarantees, and their perfection under Algerian law.
- Consumer protection laws if applicable.
- Foreign investment or currency exchange regulations if relevant.

**Perform your analysis now based ONLY and STRICTLY on the provided information from Algerian laws and regulations, DO NOT make any assumptions.**
""" 