# agent four of challlenge 3
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableLambda
from typing import Dict, List, Any
import re
import json
from dotenv import load_dotenv

load_dotenv()

def create_validation_agent():
    """
    Creates an agent responsible for validating proposed modifications to Islamic finance standards
    to ensure they align with Shariah principles, technical standards, and practical implementation.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0.1)  # Very low temperature for consistent validation

    system_prompt = """
You are a specialized Islamic Finance Standards Validation Agent. Your task is to validate proposed 
amendments to AAOIFI Financial Accounting Standards based on key elements of the original standard
and suggested modifications.

For each proposed amendment, assess the following:

1. **Conceptual Alignment**
   - Do the amendments align with the AAOIFI Conceptual Framework for Financial Reporting?
   - Evaluate alignment with recognition, measurement, presentation, and disclosure principles

2. **Shariah Compliance**
   - Are the changes consistent with applicable AAOIFI Shariah Standards (e.g., Musharaka, Ijarah, Istisna'a, Mudaraba)?
   - Verify compliance with core principles:
     - Prohibition of riba, gharar, and maysir
     - Proper risk/reward sharing
     - Valid contract formation (offer, acceptance, delivery)

3. **Technical Conformity**
   - Do the amendments conform to relevant and recent AAOIFI FAS?
   - Check alignment with standards like FAS 28 on Murabaha, FAS 30 on impairments, FAS 44-46 on control, 
     equity classification, or off-balance-sheet treatment

4. **Avoidance of Redundancy and Conflict**
   - Do the proposed changes conflict with or duplicate requirements already covered in other FAS?
   - If conflicts exist, recommend consolidation or clarification

5. **Usability and Implementation**
   - Are the amendments practically implementable by Islamic financial institutions?
   - Are disclosure or recognition rules measurable and auditable?

Provide a structured response for each amendment with:
- A clause-by-clause compliance assessment
- Any detected inconsistencies or issues
- A final judgment on whether the amendment is valid, needs revision, or should be rejected
- Citations of relevant Shariah or FAS clauses if applicable

IMPORTANT: Even with minimal information about the original standard, provide a thorough and
detailed validation based on your knowledge of Islamic finance principles and standards. Do not request
additional information - work with what you have been provided.
"""

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        HumanMessage(content="""
Based on the key elements and the suggested modifications, validate the proposed amendments to 
the AAOIFI Financial Accounting Standard under review:

1. Key elements of the original standard:
{extracted_elements}

2. Suggested modifications:
{proposed_modifications}

Please provide a structured validation assessment according to the framework.
""")
    ])

    def parse_modifications(modification_text: str) -> List[Dict[str, Any]]:
        """
        Parse the modification text to extract individual modifications
        """
        # This is a simplified parser - in a real implementation, you would use a more robust approach
        modifications = []
        sections = re.split(r'##\s+', modification_text)
        
        for section in sections[1:]:  # Skip the first empty section
            lines = section.strip().split('\n')
            title = lines[0].strip()
            
            mod = {
                'title': title,
                'reference': '',
                'current_text': '',
                'proposed_modification': '',
                'justification': '',
                'implementation': ''
            }
            
            current_field = None
            for line in lines[1:]:
                if '**Reference:**' in line:
                    current_field = 'reference'
                    mod[current_field] = line.split('**Reference:**')[1].strip()
                elif '**Current Text:**' in line:
                    current_field = 'current_text'
                    mod[current_field] = line.split('**Current Text:**')[1].strip()
                elif '**Proposed Modification:**' in line:
                    current_field = 'proposed_modification'
                elif '**Justification:**' in line:
                    current_field = 'justification'
                elif '**Implementation Considerations:**' in line:
                    current_field = 'implementation'
                elif current_field and line.strip():
                    if line.startswith('**'):
                        continue
                    mod[current_field] += line + '\n'
            
            # Clean up any trailing newlines
            for key in mod:
                if isinstance(mod[key], str):
                    mod[key] = mod[key].strip()
            
            modifications.append(mod)
        
        return modifications

    def calculate_status(scores: Dict[str, int]) -> str:
        """
        Calculate the overall status based on dimension scores
        """
        min_score = min(scores.values())
        if min_score >= 7:
            return "VALID"
        elif min_score >= 4:
            return "NEEDS REVISION"
        else:
            return "REJECT"

    def validation_logic(inputs):
        """
        Process the extracted elements and proposed modifications to validate changes.
        These inputs should come from preceding agents in the workflow.
        """
        # Provide fallback values in case inputs are missing
        extracted_elements = inputs.get("extracted_elements", "Limited information available about the original standard.")
        proposed_modifications = inputs.get("proposed_modifications", "No specific modifications provided.")
        
        # Ensure we have at least some content to work with
        if not extracted_elements.strip():
            extracted_elements = "Limited information available about the original standard."
        
        if not proposed_modifications.strip():
            return {
                "output": "Error: No proposed modifications provided. Please provide at least one modification to validate."
            }
        
        # Use the LLM for validation
        chain = prompt | llm
        
        # Get validation assessment from the LLM
        response = chain.invoke({
            "extracted_elements": extracted_elements, 
            "proposed_modifications": proposed_modifications
        })
        
        return {"output": response.content}
    
    return RunnableLambda(validation_logic)

# Example of a structured validation output processor
def parse_validation_results(validation_text: str) -> List[Dict[str, Any]]:
    """
    Parse the validation results into structured data
    Note: This is a simplified implementation - in production you would use more robust parsing
    """
    results = []
    
    # Split by modification sections
    sections = re.split(r'##\s+\d+\.\s+', validation_text)
    
    for section in sections[1:]:  # Skip the first empty section
        lines = section.strip().split('\n')
        title = lines[0].strip()
        
        result = {
            'title': title,
            'status': '',
            'scores': {},
            'recommendations': []
        }
        
        current_section = None
        for line in lines[1:]:
            if '**Status:**' in line:
                result['status'] = line.split('**Status:**')[1].strip()
            elif '**Conceptual Alignment (Score:' in line:
                score = re.search(r'Score:\s+(\d+)/10', line)
                if score:
                    result['scores']['conceptual'] = int(score.group(1))
                current_section = 'conceptual'
            elif '**Shariah Compliance (Score:' in line:
                score = re.search(r'Score:\s+(\d+)/10', line)
                if score:
                    result['scores']['shariah'] = int(score.group(1))
                current_section = 'shariah'
            elif '**Technical Conformity (Score:' in line:
                score = re.search(r'Score:\s+(\d+)/10', line)
                if score:
                    result['scores']['technical'] = int(score.group(1))
                current_section = 'technical'
            elif '**Redundancy and Conflict Analysis (Score:' in line:
                score = re.search(r'Score:\s+(\d+)/10', line)
                if score:
                    result['scores']['redundancy'] = int(score.group(1))
                current_section = 'redundancy'
            elif '**Practical Implementation Assessment (Score:' in line:
                score = re.search(r'Score:\s+(\d+)/10', line)
                if score:
                    result['scores']['implementation'] = int(score.group(1))
                current_section = 'implementation'
            elif '**Recommendations**' in line:
                current_section = 'recommendations'
            elif current_section == 'recommendations' and line.strip() and line.strip().startswith('- '):
                recommendation = line.strip()[2:].strip()
                result['recommendations'].append(recommendation)
        
        results.append(result)
    
    return results

# Function to run validation with outputs from preceding agents
def run_validation(extracted_elements, proposed_modifications):
    """
    Run validation on the outputs from preceding agents
    
    Parameters:
    - extracted_elements: Output from the first agent (key elements of original standard)
    - proposed_modifications: Output from the third agent (suggested modifications)
    
    Returns:
    - Structured validation assessment of the proposed amendments
    """
    try:
        validation_agent = create_validation_agent()
        result = validation_agent.invoke({
            "extracted_elements": extracted_elements,
            "proposed_modifications": proposed_modifications
        })
        
        # You could optionally parse the results
        # parsed_results = parse_validation_results(result["output"])
        
        return result["output"]
    except Exception as e:
        return f"Error running validation: {str(e)}"

# Example usage demonstrating how to connect outputs from preceding agents
if __name__ == "__main__":
    # These would be the outputs from your previous agents
    # Replace these with actual outputs from your preceding agents
    agent1_output = """
AAOIFI Standard on Istisna'a Contracts (FAS 11)
Section 3.1 covers the structure of Istisna'a contracts, which currently focuses on traditional paper-based documentation
and execution requirements.
"""
    
    agent3_output = """
## Digital Transaction Structures

**Reference:** Section 3.1 "Structure of Istisna'a Contracts"

**Current Text:** 
The standard currently specifies paper-based documentation requirements and physical signatures for contract validation.

**Proposed Modification:**
Add new subsection 3.1.7: "Digital Istisna'a Transactions"

"3.1.7 Islamic Financial Institutions (IFIs) may execute Istisna'a contracts through digital means, provided that:

a) The digital platform maintains complete documentation of offer, acceptance, and specifications.
b) Electronic signatures comply with relevant jurisdictional e-signature laws.
c) The system ensures that all contract terms are disclosed and explicitly agreed upon by both parties.
d) The digital platform must maintain immutable records of all contract terms, modifications, and fulfillment stages.
e) Smart contract implementations must include code audits by Shariah experts to ensure compliance."

**Justification:**
This modification aligns with the AAOIFI Shariah Standard No. 5 on "Guarantees" which acknowledges modern commercial practices while maintaining the essence of Islamic contracts.

**Implementation Considerations:**
- IFIs will need to ensure digital platforms are certified for Shariah compliance
- Contract audit trails must be maintained for the duration specified in original paper requirements
"""
    
    # Run the validation using outputs from preceding agents
    result = run_validation(agent1_output, agent3_output)
    print(result)