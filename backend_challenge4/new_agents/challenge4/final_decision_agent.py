import os
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from ..custom_chat_models.chat_openrouter import ChatOpenRouter
from .base_agent import BaseAgent

# Load environment variables
load_dotenv()

# Use a capable model for summarizing complex data
MODEL_NAME = "openai/gpt-4o-mini"

# Define structured output schema using Pydantic
class DecisionSummary(BaseModel):
    """Schema for the final decision summary output."""
    executive_summary: str = Field(
        description="Comprehensive 3-4 paragraph summary of the entire process and outcome"
    )
    key_findings: List[str] = Field(
        description="List of key findings from all evaluations",
        min_items=3,
        max_items=10
    )
    recommendations: List[str] = Field(
        description="List of actionable recommendations for implementation",
        min_items=3,
        max_items=10
    )
    potential_challenges: List[str] = Field(
        description="List of potential challenges that may arise during implementation",
        min_items=2,
        max_items=7
    )
    next_steps: List[str] = Field(
        description="List of suggested next steps for the client",
        min_items=3,
        max_items=7
    )
    overall_assessment: str = Field(
        description="Final verdict on the project (APPROVED, CONDITIONALLY APPROVED, or REJECTED)"
    )
    confidence_level: str = Field(
        description="Confidence level in the assessment (High, Medium, or Low)"
    )

class FinalDecisionAgent(BaseAgent):
    agent_name = "FinalDecisionAgent"

    def __init__(self):
        super().__init__()
        self.llm = ChatOpenRouter(model_name=MODEL_NAME, temperature=0.2)
        # Create a structured output version of the LLM
        self.structured_llm = self.llm.with_structured_output(DecisionSummary)
        print(f"{self.agent_name} initialized.")

    def _perform_task(self, pco: dict):
        """Generate a comprehensive summary of the PCO after all agents have executed."""
        pco["processing_log"][-1]["message"] = "Generating final decision and summary..."
        
        # Build a prompt from PCO data
        prompt = self._build_summary_prompt(pco)
        
        # Generate the structured summary using LLM
        try:
            # Use the structured output LLM to enforce the schema
            summary_result = self.structured_llm.invoke(prompt)
            
            # Store the structured result in the PCO
            pco["final_decision_report"] = {
                "executive_summary": summary_result.executive_summary,
                "key_findings": summary_result.key_findings,
                "recommendations": summary_result.recommendations,
                "potential_challenges": summary_result.potential_challenges,
                "next_steps": summary_result.next_steps,
                "overall_assessment": summary_result.overall_assessment,
                "confidence_level": summary_result.confidence_level,
                "status": "COMPLETED"
            }
            
            # Update PCO status
            pco["current_status"] = "completed"
            pco["processing_log"][-1]["message"] = "Final summary and decision generated successfully."
            
        except Exception as e:
            error_message = f"Error generating final summary: {str(e)}"
            pco["processing_log"][-1]["message"] = error_message
            pco["error_info"] = {"stage": "final_decision", "details": error_message}
            pco["current_status"] = "error"

    def _build_summary_prompt(self, pco: dict) -> str:
        """Build a comprehensive prompt for the LLM to generate a summary of the PCO."""
        # Extract key data from PCO
        client_details = pco.get("client_details", {})
        project_details = pco.get("project_details", {})
        enterprise_audit = pco.get("enterprise_audit_results", {})
        project_evaluation = pco.get("project_evaluation_results", {})
        contract_details = pco.get("selected_contract_details", {})
        formalized_contract = pco.get("formalized_contract", {})
        accounting_report = pco.get("accounting_entries_report", {})
        shariah_report = pco.get("shariah_compliance_report", {})
        country_law_report = pco.get("country_law_validation_report", {})
        
        # Construct the prompt
        prompt = f"""You are the final decision-making agent in an Islamic finance advisory system. 
You need to create a comprehensive executive summary of the entire process and outcomes.

## CLIENT INFORMATION
Client: {client_details.get('client_name', 'N/A')}
Type: {client_details.get('client_type', 'N/A')}
Industry: {client_details.get('industry', 'N/A')}
Experience: {client_details.get('experience', 'N/A')}

## PROJECT DETAILS
Project Name: {project_details.get('project_name', 'N/A')}
Description: {project_details.get('description', 'N/A')}
Sector: {project_details.get('sector', 'N/A')}
Location: {project_details.get('location', 'N/A')}
Estimated Cost: {project_details.get('estimated_cost', 'N/A')}
Expected Revenue: {project_details.get('expected_revenue', 'N/A')}
Duration: {project_details.get('duration_months', 'N/A')} months
Objective: {project_details.get('objective', 'N/A')}

## ANALYSIS RESULTS
Enterprise Audit Verdict: {enterprise_audit.get('verdict', 'N/A')}
Enterprise Audit Score: {enterprise_audit.get('score', 'N/A')}
Enterprise Audit Summary: {enterprise_audit.get('summary', 'N/A')}

Project Evaluation Decision: {project_evaluation.get('decision', 'N/A')}
Project Viability: {project_evaluation.get('is_viable', 'N/A')}
Project Evaluation Justification: {project_evaluation.get('justification', 'N/A')}
Identified Risks: {project_evaluation.get('identified_risks', 'N/A')}
Shariah Preliminary Fit: {project_evaluation.get('shariah_preliminary_fit', 'N/A')}

## CONTRACT INFORMATION
Selected Contract Type: {contract_details.get('primary_contract_type', 'N/A')}
Contract Justification: {contract_details.get('justification', 'N/A')}
Key Parameters: {contract_details.get('key_parameters_required', 'N/A')}
Relevant AAOIFI Standards: {contract_details.get('relevant_aaoifi_fas', 'N/A')}

Formalized Contract: {formalized_contract.get('summary', 'Available' if formalized_contract else 'Not Available')}

## COMPLIANCE AND VALIDATION
Accounting Treatment: {accounting_report.get('summary', 'Available' if accounting_report else 'Not Available')}
Shariah Compliance: {shariah_report.get('is_compliant', 'N/A') if shariah_report else 'Not Evaluated'}
Shariah Report Summary: {shariah_report.get('summary', 'N/A') if shariah_report else 'Not Available'}
Country Law Validation: {country_law_report.get('is_compliant', 'N/A') if country_law_report else 'Not Evaluated'}
Country Law Report Summary: {country_law_report.get('summary', 'N/A') if country_law_report else 'Not Available'}

Based on all the above information, provide a structured analysis in the required JSON format with:

1. A detailed executive summary (3-4 paragraphs)
2. Key findings from all evaluations (bullet points)
3. Recommendations for implementation (bullet points)
4. Potential challenges that may arise (bullet points)
5. Next steps for the client (bullet points)
6. An overall assessment (APPROVED, CONDITIONALLY APPROVED, or REJECTED)
7. A confidence level in your assessment (High, Medium, or Low)

Make your summary comprehensive, highlighting the most important aspects from each evaluation stage.
"""
        return prompt