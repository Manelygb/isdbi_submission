from .base_agent import BaseAgent
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.chat_models import ChatOpenAI
import json
import os
import datetime

class ShariahComplianceValidatorAgent(BaseAgent):
    agent_name = "ShariahComplianceValidatorAgent"

    def _load_standards_retriever(self):
        # Make the path absolute relative to this script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        index_dir = os.path.join(script_dir, "../../vector_storee/standards")
        
        if not os.path.exists(index_dir):
            # Log error in PCO instead of raising exception
            return None
            
        try:
            embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")
            retriever = FAISS.load_local(
                index_dir, embeddings, allow_dangerous_deserialization=True
            ).as_retriever()
            return retriever
        except Exception as e:
            # Log error instead of breaking execution
            return None

    def _detect_non_compliance(self, text, retriever, llm):
        if not retriever:
            return [{"error": "Vector store not available", "message": "Unable to load standards database"}]
            
        try:
            docs = retriever.invoke(text)
            context = "\n\n".join([
                f"[Source: {doc.metadata.get('source', 'Unknown')}, Page: {doc.metadata.get('page', 'N/A')}]\n{doc.page_content}"
                for doc in docs
            ])

            messages = [
                SystemMessage(content="""
You are a Shariah compliance reviewer. Your task is to analyze the input contract or scenario and identify clauses that may violate Islamic finance principles such as:
- **Riba** (interest-based terms)
- **Gharar** (excessive uncertainty)
- **Maysir** (speculation or gambling)

Use the **AAOIFI context excerpts** provided to support your findings. The context may contain metadata such as the source document name and page number in this format:

    [Source: fas_28, Page: 3]
    Text content from that page...

Please cite the **actual source and page number** in your response whenever a match is found.

Return your results as a **JSON array**, with each object structured as follows:

[
  {
    "issue": "Concise title of the violation (e.g., 'Gharar in commodity terms')",
    "quote": "Exact clause or sentence from the input that violates Shariah",
    "justification": "Why it violates Shariah, with reference to Islamic finance rules",
    "reference": "Use the [Source: ..., Page: ...] metadata closest to the relevant supporting excerpt. If no metadata match is clear, return 'Unverified'."
  }
]

If no issues are found, return an empty array [].
"""),
                HumanMessage(content=f"Text to Review:\n{text}\n\nAAOIFI Context:\n{context}")
            ]
            response = llm.invoke(messages)
            
            try:
                import re
                match = re.search(r"\[\s*{.*?}\s*\]", response.content, re.DOTALL)
                if match:
                    parsed = json.loads(match.group(0))
                    return parsed
                # fallback: try direct parse
                parsed = json.loads(response.content.strip())
                return parsed
            except Exception:
                return [{"error": "Could not parse LLM response", "raw": response.content}]
        except Exception as e:
            return [{"error": "Error during compliance detection", "message": str(e)}]

    def _propose_fixes(self, issues, llm):
        try:
            messages = [
                SystemMessage(content="""
You are an Islamic finance contract improver. For each non-compliant issue, suggest a revised version and explain how it now meets AAOIFI standards.

Return a JSON list:
[
  {
    "original": "...",
    "suggestion": "...",
    "explanation": "Shariah-compliant justification"
  }
]
Only return the JSON array, with no extra text or explanation.
"""),
                HumanMessage(content=json.dumps(issues, indent=2))
            ]
            response = llm.invoke(messages)
            
            try:
                import re
                match = re.search(r"\[\s*{.*?}\s*\]", response.content, re.DOTALL)
                if match:
                    parsed = json.loads(match.group(0))
                    return parsed
                # fallback: try direct parse
                parsed = json.loads(response.content.strip())
                return parsed
            except Exception:
                return [{"error": "Could not parse enhancement response", "raw": response.content}]
        except Exception as e:
            return [{"error": "Error generating fixes", "message": str(e)}]

    def _perform_task(self, pco: dict):
        # Update status in processing log
        pco["processing_log"].append({
            "agent": self.agent_name,
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "Starting Shariah compliance validation.",
            "status": "in_progress"
        })
        
        # Get formalized contract from PCO
        contract = pco.get("formalized_contract", {})
        if not contract:
            pco["shariah_compliance_report"] = {
                "status": "error",
                "message": "No formalized contract found in PCO",
                "timestamp": datetime.datetime.now().isoformat()
            }
            pco["current_status"] = "error_in_shariah_validation"
            return pco
            
        text = contract.get("document_text", "") or contract.get("document_text_summary", "")
        if not text:
            pco["shariah_compliance_report"] = {
                "status": "error",
                "message": "No contract text found in formalized contract",
                "timestamp": datetime.datetime.now().isoformat()
            }
            pco["current_status"] = "error_in_shariah_validation"
            return pco
        
        # Set up retriever and LLM
        retriever = self._load_standards_retriever()
        
        # Use the default OpenAI model or fallback
        try:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(temperature=0.2)
        except Exception:
            # Fallback to the community version
            llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.2
            )
            
        # Run compliance check
        issues = self._detect_non_compliance(text, retriever, llm)
        
        # Check for errors
        if issues and any("error" in issue for issue in issues):
            error_issues = [i for i in issues if "error" in i]
            pco["shariah_compliance_report"] = {
                "status": "error",
                "message": "Error during Shariah compliance checking",
                "details": error_issues,
                "timestamp": datetime.datetime.now().isoformat()
            }
            pco["current_status"] = "error_in_shariah_validation"
            return pco
            
        # If no real issues found (empty list or no actual violations)
        if not issues or len(issues) == 0:
            pco["shariah_compliance_report"] = {
                "status": "compliant",
                "message": "No Shariah compliance issues detected",
                "details": [],
                "overall_status": "PASS",
                "timestamp": datetime.datetime.now().isoformat()
            }
            pco["current_status"] = "pending_country_law_validation"
            return pco
            
        # Generate fixes for issues
        suggestions = self._propose_fixes(issues, llm)
        
        # Create full compliance report
        pco["shariah_compliance_report"] = {
            "status": "non_compliant",
            "message": f"Found {len(issues)} Shariah compliance issues",
            "issues": issues,
            "suggested_fixes": suggestions,
            "overall_status": "FAIL",
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Update status to proceed to next agent
        pco["current_status"] = "pending_country_law_validation"
        
        return pco