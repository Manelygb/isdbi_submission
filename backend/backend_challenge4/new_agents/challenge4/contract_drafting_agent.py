import os
import json
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from ..custom_chat_models.chat_openrouter import ChatOpenRouter
from .base_agent import BaseAgent

# Load environment variables from .env file
load_dotenv()

MODEL_NAME = "deepseek/deepseek-chat-v3-0324"  # Use deepseek model like the enterprise_audit_agent

class ContractDraftingAgent(BaseAgent):
    agent_name = "ContractDraftingAgent"

    def __init__(self):
        super().__init__()
        self.llm = ChatOpenRouter(model_name=MODEL_NAME, temperature=0.3)
        print(f"{self.agent_name} initialized.")
        
    def _perform_task(self, pco: dict):
        pco["processing_log"][-1]["message"] = "Starting contract drafting..."
        
        try:
            # Extract project details and selected contract information
            project_details = pco.get("project_details", {})
            client_details = pco.get("client_details", {})
            project_evaluation = pco.get("project_evaluation_results", {})
            enterprise_audit = pco.get("enterprise_audit_results", {})
            selected_contract = pco.get("selected_contract_details", {})
            
            if not selected_contract:
                raise ValueError("Missing contract selection in PCO")
                
            # Get primary contract type
            primary_contract = selected_contract.get("primary_contract_type", "Unknown")
            
            # Retrieve contract information using the knowledge base
            contract_info = self._get_contract_information(primary_contract)
            
            # Format information for the LLM
            formatted_data = self._format_data_for_llm(
                project_details, 
                client_details, 
                project_evaluation, 
                enterprise_audit, 
                selected_contract,
                contract_info
            )
            
            # Generate contract draft
            contract_draft = self._generate_contract_draft(formatted_data)
            
            # Process the contract content to ensure proper formatting
            processed_content = self._process_contract_content(contract_draft)
            
            # Update PCO with the drafted contract
            pco["contract_draft"] = {
                "content": processed_content,
                "contract_type": primary_contract,
                "version": "1.0",
                "status": "draft_completed"
            }
            
            # Also create the formalized_contract field that downstream agents expect
            pco["formalized_contract"] = {
                "document_text_summary": processed_content,
                "contract_type": primary_contract,
                "version": "1.0",
                "status": "formalized",
                "signed_date": None  # Would be populated after actual signing
            }
            
            pco["current_status"] = "pending_accounting_generation"
            pco["processing_log"][-1]["message"] = f"Contract draft completed for {primary_contract} contract."
            
        except Exception as e:
            error_message = f"Error during contract drafting: {str(e)}"
            pco["contract_draft"] = {
                "content": None,
                "status": "draft_failed",
                "error": error_message
            }
            pco["current_status"] = "error_contract_drafting"
            pco["processing_log"][-1]["message"] = error_message
            print(f"Critical error in ContractDraftingAgent: {e}")
    
    def _get_contract_information(self, contract_type: str) -> str:
        """Retrieves information about the specified contract type from the knowledge base."""
        try:
            # Initialize embeddings and vector store
            embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
            
            # Try loading vector store from either location
            try:
                vector_store = FAISS.load_local(
                    "vector_storee/index",
                    embeddings,
                    allow_dangerous_deserialization=True
                )
            except Exception as e:
                print(f"Unable to load from first location, trying alternative: {e}")
                vector_store = FAISS.load_local(
                    "../vector_storee/index",
                    embeddings,
                    allow_dangerous_deserialization=True
                )
            
            # Create retriever and QA chain
            retriever = vector_store.as_retriever()
            qa_chain = RetrievalQA.from_chain_type(
                llm=ChatOpenRouter(model_name=MODEL_NAME),
                retriever=retriever
            )
            
            # Query for contract information
            contract_info_query = f"""
            What are the key requirements, structure, and implementation details for {contract_type} 
            according to AAOIFI standards? Include:
            1. Essential elements of the contract
            2. Required conditions and steps
            3. Prohibited elements to avoid
            4. Typical payment and profit structures
            5. Risk management considerations
            6. Common supporting contracts
            7. Specific Shariah compliance requirements
            """
            
            contract_info = qa_chain.invoke(contract_info_query)
            
            return contract_info.get("result", "No information found.")
            
        except Exception as e:
            print(f"Error retrieving contract information: {e}")
            # Return fallback information to allow the agent to continue even if the vector store fails
            return self._get_fallback_contract_info(contract_type)
    
    def _get_fallback_contract_info(self, contract_type: str) -> str:
        """Provides basic fallback information for common contract types."""
        fallback_info = {
            "Istisna'a": """
            Istisna'a is a contract for manufacturing or construction where one party agrees to produce or build a specified item for another. 
            Key requirements include: detailed specifications must be agreed upfront, price must be fixed, quality standards clearly defined, 
            delivery timeline established, and ownership transfers upon completion. Typically implemented with a parallel Istisna'a where the 
            bank acts as an intermediary between client and manufacturer/contractor. Related AAOIFI standard is FAS 10.
            """,
            "Murabaha": """
            Murabaha is a cost-plus sale contract where the bank purchases an asset and sells it to the client at a marked-up price with deferred payment.
            Key requirements include: bank must actually own the asset before selling, cost and profit margin must be clearly disclosed, 
            sale must occur after bank ownership, and asset must be clearly identified. Typically used for tangible assets.
            Related AAOIFI standards are FAS 2 and FAS 1.
            """,
            "Musharakah": """
            Musharakah is a partnership contract where parties contribute capital to a joint venture, sharing profits according to pre-agreed ratios
            and losses according to capital contribution. Key requirements include: clear capital contributions, profit-sharing ratio determined upfront, 
            management rights defined, and exit mechanisms established. Used for both short and long-term investment projects.
            Related AAOIFI standard is FAS 4.
            """,
            "Ijarah": """
            Ijarah is a lease contract where the bank purchases an asset and leases it to the client for a specified period with fixed rental payments.
            Key requirements include: asset must be owned by lessor, usufruct transfers to lessee, rental amount and period must be defined, 
            and maintenance responsibilities clearly allocated. Can be used with Ijarah Muntahia Bittamleek (lease ending with ownership).
            Related AAOIFI standard is FAS 8.
            """,
            "Salam": """
            Salam is a forward purchase contract where payment is made in full at the time of contract while delivery of commodity is deferred.
            Key requirements include: full payment at contract signing, commodity must be standardizable, quantity and quality must be specified,
            and delivery date must be fixed. Often used with parallel Salam to mitigate market risk.
            Related AAOIFI standard is FAS 7.
            """
        }
        
        # Return information for the specified contract type or a general message
        return fallback_info.get(
            contract_type, 
            f"Basic information about {contract_type}: This is an Islamic financial contract that must comply with Shariah principles prohibiting interest, excessive uncertainty, and gambling. Specific implementation details should follow relevant AAOIFI standards."
        )
    
    def _format_data_for_llm(
        self,
        project_details: dict,
        client_details: dict,
        project_evaluation: dict,
        enterprise_audit: dict,
        selected_contract: dict,
        contract_info: str
    ) -> dict:
        """Formats all the data for the LLM prompt."""
        
        # Format project description
        project_description = f"""
        Project Name: {project_details.get('project_name', 'Untitled Project')}
        Objective: {project_details.get('objective', 'N/A')}
        Sector: {project_details.get('sector', 'N/A')}
        Location: {project_details.get('location', 'N/A')}
        Estimated Cost: ${project_details.get('estimated_cost', 0):,}
        Expected Revenue: ${project_details.get('expected_revenue', 0):,}
        Timeline: {project_details.get('payback_period', 0)} years
        Risks: {project_details.get('risks', 'None specified')}
        """
        
        # Format client details
        client_description = f"""
        Client Type: {client_details.get('client_type', 'N/A')}
        Experience: {client_details.get('experience', 'N/A')}
        """
        
        if client_details.get('client_type') == 'company':
            client_description += f"""
            Financial Health: {enterprise_audit.get('summary', 'No audit summary available')}
            Financial Score: {enterprise_audit.get('score', 'N/A')}
            """
        
        # Format evaluation results
        evaluation_description = f"""
        Decision: {project_evaluation.get('decision', 'N/A')}
        Confidence: {project_evaluation.get('confidence', 0)}
        Justification: {project_evaluation.get('justification', 'No justification provided')}
        Identified Risks: {', '.join(project_evaluation.get('identified_risks', ['None']))}
        Shariah Preliminary Fit: {project_evaluation.get('shariah_preliminary_fit', 'Not assessed')}
        """
        
        # Format contract selection details
        contract_selection = f"""
        Primary Contract Type: {selected_contract.get('primary_contract_type', 'N/A')}
        Justification: {selected_contract.get('justification', 'No justification provided')}
        Required Parameters: {', '.join(selected_contract.get('key_parameters_required', ['None']))}
        Relevant AAOIFI Standards: {', '.join(selected_contract.get('relevant_aaoifi_fas', ['None']))}
        """
        
        return {
            "project_description": project_description,
            "client_description": client_description,
            "evaluation_results": evaluation_description,
            "contract_selection": contract_selection,
            "contract_info": contract_info,
            "primary_contract": selected_contract.get('primary_contract_type', 'Unknown')
        }
    
    def _generate_contract_draft(self, formatted_data: dict) -> str:
        """Generates the contract draft using the LLM."""
        
        # Enhanced system prompt with examples
        system_prompt = """
You are a specialized Shariah-compliant contract drafting assistant with expertise in Islamic finance documentation.

## Your Task:
Create a formal, professionally-worded financing scenario describing how an Islamic financial institution would structure and implement the recommended Islamic contract for the given project.

## Input Information:
1. Project description (purpose, costs, parties involved)
2. Primary Islamic contract type identified in the evaluation (e.g., Murabaha, Ijarah, Istisna'a, Musharaka, Salam)
3. Full financial assessment including justification, structure details, and compliance considerations

## Output Requirements:
Produce a detailed, realistic financing scenario that:
- Is structured like an official Islamic financing document summary
- Explains precisely how the specific Islamic contract will be implemented
- Includes all mandatory elements required for Shariah compliance
- Specifies the roles and responsibilities of all parties
- Outlines the financial flow and payment structure
- Addresses key risk considerations and their mitigations
- Includes any necessary supporting contracts or arrangements

## OUTPUT FORMAT:
IMPORTANT: Do NOT use triple backticks (```) in your response. Output the content directly as markdown.

# ISLAMIC FINANCING SCENARIO: [CONTRACT TYPE]

## CONTRACT OVERVIEW
[Concise explanation of how this contract structure will be applied to finance the project]

## CONTRACT STRUCTURE
- **Contract Type:** [Primary contract and any supporting arrangements]
- **Parties:** [Define roles of each party]
- **Subject Matter:** [Description of the asset/service/project being financed]
- **Timeline:** [Key phases of the contract execution]

## FINANCIAL STRUCTURE
- **Total Financing Amount:** [From project description]
- **Payment Mechanism:** [Details of how payments will be structured]
- **Profit/Return Structure:** [How returns are calculated and distributed]
- **Risk Distribution:** [How risks are allocated between parties]

## KEY CONTRACT PROVISIONS
[List 5-7 critical contract provisions with brief explanations]

## SHARIAH COMPLIANCE SAFEGUARDS
[List specific measures to ensure Shariah compliance]

## EXECUTION PROCESS
[Step-by-step implementation process]

## Example Contract Scenarios:

### Example 1: Istisna'a Contract for Factory Construction

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

## KEY CONTRACT PROVISIONS
1. Detailed specifications must be agreed upon before contract execution (AAOIFI FAS 10)
2. Title transfers only upon final acceptance and delivery of the completed facility
3. Progress inspections scheduled at 25%, 50%, 75%, and 100% completion
4. Late delivery penalties apply to contractor but not passed to end client
5. Force majeure clauses protect against uncontrollable events
6. Quality assurance provisions with independent verification
7. Contractor replacement clause if performance is inadequate

## SHARIAH COMPLIANCE SAFEGUARDS
1. No interest-based penalties for late payment (alternative compensation mechanism used)
2. Clear separation of Istisna'a and Parallel Istisna'a contracts
3. Bank must actually own the asset during construction phase
4. Price is fixed and known at contract inception
5. Subject of manufacture must be precisely specified
6. Independent Shariah review of contract documentation

## EXECUTION PROCESS
1. Client submits detailed facility specifications and requirements
2. Bank evaluates project viability and approves financing
3. Bank executes Istisna'a contract with client (buyer)
4. Bank executes Parallel Istisna'a with contractor
5. Contractor begins construction with bank's upfront payment
6. Bank conducts periodic inspections to verify progress
7. Upon completion, bank accepts delivery from contractor
8. Client inspects and accepts the facility from bank
9. Client begins quarterly payments to bank

### Example 2: Murabaha Contract for Equipment Purchase

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

## KEY CONTRACT PROVISIONS
1. Equipment must be owned by bank before Murabaha sale (AAOIFI FAS 2)
2. Cost and profit components must be explicitly disclosed
3. Down payment of 10% ($50,000) required from client
4. Late payment donations to charity rather than penalties to bank
5. Equipment serves as collateral until full payment
6. Insurance costs borne by client after purchase
7. Equipment specifications and warranties pass through to client

## SHARIAH COMPLIANCE SAFEGUARDS
1. Separate purchase and sale contracts executed in correct sequence
2. Ownership risk borne by bank before client purchase
3. Asset must be in existence and specified at time of Murabaha
4. No interest-based penalties for late payment
5. Pre-payment rebates at bank's discretion
6. Shariah audit of transaction documentation and execution

## EXECUTION PROCESS
1. Client identifies equipment and supplier; requests Murabaha financing
2. Bank approves financing application after credit assessment
3. Client signs binding promise to purchase
4. Bank purchases equipment from supplier
5. Bank takes constructive or physical possession
6. Bank sells equipment to client through Murabaha agreement
7. Client makes down payment and begins monthly installments
8. Title transfers to client while bank maintains security interest

## Guidelines:
- Use formal, precise language like official Islamic financing documentation
- Include only information present in the inputs—do not invent specific dates, client names, or exact values not provided
- Explicitly reference relevant AAOIFI standards in your explanations
- Ensure the scenario is logically coherent and complies with all Shariah principles
- Address potential issues identified in the financial assessment
- Describe how any risks or compliance concerns will be mitigated
- Focus on the practical implementation details a bank would need to follow
- DO NOT wrap your response in triple backticks (```) - provide the content directly
"""

        # Human prompt template
        human_prompt = """
Please create a detailed Islamic financing scenario based on the following information:

PROJECT DESCRIPTION:
{project_description}

CLIENT INFORMATION:
{client_description}

EVALUATION RESULTS:
{evaluation_results}

RECOMMENDED CONTRACT TYPE:
{primary_contract}

CONTRACT SELECTION DETAILS:
{contract_selection}

ADDITIONAL CONTRACT INFORMATION:
{contract_info}

Create a professional, Shariah-compliant financing scenario following the required output format. Include all required elements of the {primary_contract} contract structure and implementation process.

IMPORTANT: Do NOT use triple backticks (```) in your response. Output the content directly as markdown.
"""

        # Format the prompt with input data
        formatted_prompt = human_prompt.format(
            project_description=formatted_data["project_description"],
            client_description=formatted_data["client_description"],
            evaluation_results=formatted_data["evaluation_results"],
            primary_contract=formatted_data["primary_contract"],
            contract_selection=formatted_data["contract_selection"],
            contract_info=formatted_data["contract_info"]
        )
        
        # Generate the contract scenario
        response = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=formatted_prompt)
        ])
        
        return response.content
    
    def _process_contract_content(self, content: str) -> str:
        """
        Process the contract content to ensure proper formatting:
        1. Remove any triple backticks at the beginning/end
        2. Ensure proper markdown formatting
        3. Handle any special characters
        """
        # Remove triple backticks if they exist at the beginning or end
        content = content.strip()
        
        # Remove leading and trailing markdown code block markers
        if content.startswith("```"):
            # Find the end of the first code block marker
            first_line_end = content.find("\n")
            if first_line_end != -1:
                content = content[first_line_end + 1:]
        
        if content.endswith("```"):
            # Find the start of the last code block marker
            last_backtick_start = content.rfind("```")
            if last_backtick_start != -1:
                content = content[:last_backtick_start].strip()
        
        # Ensure proper line endings
        content = content.replace("\r\n", "\n").replace("\r", "\n")
        
        # Ensure there are no consecutive blank lines (more than 2)
        while "\n\n\n" in content:
            content = content.replace("\n\n\n", "\n\n")
        
        # Ensure proper heading formatting (space after #)
        lines = content.split("\n")
        for i in range(len(lines)):
            if lines[i].startswith("#"):
                # Count the number of # characters
                count = 0
                while count < len(lines[i]) and lines[i][count] == '#':
                    count += 1
                
                # If there's no space after the # characters, add one
                if count < len(lines[i]) and lines[i][count] != ' ':
                    lines[i] = lines[i][:count] + ' ' + lines[i][count:]
        
        # Rejoin the lines
        content = "\n".join(lines)
        
        return content 