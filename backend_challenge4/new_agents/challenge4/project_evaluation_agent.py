import os
import json
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from ..custom_chat_models.chat_openrouter import ChatOpenRouter
from .base_agent import BaseAgent

# Load environment variables from .env file
load_dotenv()

MODEL_NAME = "openai/gpt-4o-mini"
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"

class EvaluationResult(BaseModel):
    decision: str = Field(description="Final decision: APPROVE, REJECT, or MODIFY")
    probability: float = Field(description="Confidence score between 0 and 1")
    justification: str = Field(description="Detailed explanation of the evaluation decision")
    identified_risks: List[str] = Field(description="List of identified risks for the project")
    shariah_preliminary_fit: str = Field(description="Initial assessment of Shariah compliance")

class ProjectEvaluationAgent(BaseAgent):
    agent_name = "ProjectEvaluationAgent"

    def __init__(self, vector_store_path="../../vector_storee/global_project_faiss_index"):
        super().__init__()
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        
        # Adjust path to be relative to this file's location
        script_dir = os.path.dirname(__file__)
        self.db_path = os.path.join(script_dir, vector_store_path)
        
        if not os.path.exists(self.db_path) or not os.path.isdir(self.db_path):
            print(f"Warning: FAISS vector store not found at {self.db_path}. Will create empty vector store for testing.")
            # In production, this would raise an error
            self.vector_store = None
        else:
            self.vector_store = FAISS.load_local(self.db_path, self.embeddings, allow_dangerous_deserialization=True)
        
        # Initialize LLM
        self.llm = ChatOpenRouter(model_name=MODEL_NAME, temperature=0.3)
        self.structured_llm = self.llm.with_structured_output(EvaluationResult)
        
        print(f"{self.agent_name} initialized.")

    def _perform_task(self, pco: dict):
        pco["processing_log"][-1]["message"] = "Starting project evaluation..."
        
        try:
            project_details = pco.get("project_details", {})
            client_details = pco.get("client_details", {})
            
            if not project_details:
                raise ValueError("Missing project details in PCO")
            
            # Format the project for evaluation
            project_text = self._format_project_text(project_details, client_details)
            
            # Run pre-checks
            flags = self._run_prechecks(project_details, client_details)
            flag_summary = "\n".join([f"- {flag}" for flag in flags]) if flags else "None"
            
            # Retrieve similar projects if vector store is available
            retrieved_summary = "No historical project data available."
            if self.vector_store:
                try:
                    retrieved_docs = self.vector_store.similarity_search(project_text, k=3)
                    retrieved_summary = "\n---\n".join([doc.page_content for doc in retrieved_docs])
                except Exception as e:
                    print(f"Error retrieving similar projects: {e}")
                    retrieved_summary = "Error retrieving similar projects."
            
            # Build prompt and run LLM evaluation
            prompt = self._build_prompt(project_text, retrieved_summary, flag_summary)
            evaluation_result = self.structured_llm.invoke(prompt)
            
            # Update PCO with evaluation results
            pco["project_evaluation_results"] = {
                "is_viable": evaluation_result.decision != "REJECT",
                "decision": evaluation_result.decision,
                "confidence": evaluation_result.probability,
                "justification": evaluation_result.justification,
                "identified_risks": evaluation_result.identified_risks,
                "shariah_preliminary_fit": evaluation_result.shariah_preliminary_fit
            }
            
            # Update PCO status based on evaluation
            if evaluation_result.decision == "REJECT":
                pco["current_status"] = "project_rejected_evaluation"
                pco["processing_log"][-1]["message"] = "Project evaluated as NOT viable."
            else:
                pco["current_status"] = "pending_contract_selection"
                pco["processing_log"][-1]["message"] = "Project evaluated as viable."
                
        except Exception as e:
            error_message = f"Error during project evaluation: {str(e)}"
            pco["project_evaluation_results"] = {
                "is_viable": False,
                "decision": "ERROR",
                "justification": error_message,
                "identified_risks": ["Evaluation process failed"],
                "shariah_preliminary_fit": "Undetermined due to error"
            }
            pco["current_status"] = "error_project_evaluation"
            pco["processing_log"][-1]["message"] = error_message
            print(f"Critical error in ProjectEvaluationAgent: {e}")
    
    def _format_project_text(self, project_details: dict, client_details: dict) -> str:
        """Format project details into a text representation for retrieval and evaluation."""
        return f"""
Project Title: {project_details.get('project_name', 'Untitled')}
Sector: {project_details.get('sector', 'Unknown')}
Location: {project_details.get('location', 'Unknown')}
Estimated Cost: ${project_details.get('estimated_cost', 0):,}
Expected Annual Revenue: ${project_details.get('expected_revenue', 0):,}
Payback Period: {project_details.get('payback_period', 0)} years
Client Experience: {client_details.get('experience', 'Unknown')}
Risks: {project_details.get('risks', 'Unknown')}
Objective: {project_details.get('objective', 'Not specified')}
"""
    
    def _run_prechecks(self, project_details: dict, client_details: dict) -> List[str]:
        """Run automated pre-checks to flag potential issues."""
        flags = []
        
        # Financial checks
        if project_details.get('payback_period', 0) > 10:
            flags.append("Long payback period (>10 years)")
            
        cost = project_details.get('estimated_cost', 0)
        revenue = project_details.get('expected_revenue', 0)
        if cost > 0 and revenue / cost < 0.3:
            flags.append("Low revenue-to-cost ratio (<0.3)")
            
        # Experience checks
        experience = client_details.get('experience', '').lower()
        if 'no experience' in experience or 'first-time' in experience:
            flags.append("No relevant sector experience")
            
        # Risk checks
        risks = project_details.get('risks', '')
        if risks:
            risk_count = len(risks.split(';'))
            if risk_count > 3:
                flags.append(f"High number of listed risks ({risk_count})")
                
        return flags
    
    def _build_prompt(self, project_text: str, similar_projects: str, precheck_flags: str) -> str:
        """Build the prompt for the LLM evaluation."""
        return f"""You are a senior project evaluation officer at an Islamic financial institution. 
Your task is to assess this project proposal using internal pre-checks and similar project history.

Pre-check flags (automatic screening):
{precheck_flags}

New project details:
{project_text}

Similar past projects:
{similar_projects}

Analyze the viability of this project, considering:
1. Financial metrics (cost, revenue, payback period)
2. Market potential and risks
3. Client experience and credibility
4. Preliminary Shariah compliance assessment

Based on all available information, determine whether to APPROVE, REJECT, or MODIFY the project.
If MODIFY, explain specific changes needed.

Your analysis should be thorough, balanced, and data-driven.
""" 