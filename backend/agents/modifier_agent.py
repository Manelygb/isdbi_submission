# agent three of challenge 3
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()

def create_modification_agent():
    """
    Creates an agent responsible for suggesting modifications to Islamic finance standards
    based on the extracted key elements and identified gaps.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)  # Lower temperature for more precise outputs

    system_prompt = """
You are a specialized Islamic Finance Standards Modification Agent. Your task is to propose specific, concrete 
modifications to AAOIFI standards that address identified gaps while maintaining compliance with Shariah principles 
and regulatory requirements.

For each gap identified in the gap analysis, propose specific modifications that would address the gap. 
Your modifications should:

1. Reference the specific section/clause of the original standard being modified (if applicable)
2. Provide exact wording for proposed additions or changes
3. Include clear justification for the modification
4. Cite relevant Shariah principles, scholarly opinions, regulatory requirements, or market developments
5. Explain how the modification maintains consistency with Islamic finance principles

Ensure that your modifications address these key areas from the gap analysis:

- Emerging financial products (digital assets, green financing, etc.)
- Digital transaction structures and smart contracts
- Blockchain-based risk solutions
- Compliance with updated regulations (IFRS updates, Basel III)
- Digital asset regulations and cross-border legal considerations
- Market trends (digital assets, crowdfunding, Sukuk markets)
- Integration of technological innovations (blockchain, AI, smart contracts)
- Adaptability to rapidly changing market conditions
- Incorporation of new Shariah rulings
- Operational guidelines for emerging sectors
- Monitoring and evaluation tools
- Improved clarity in terminology and definitions

Format each proposed modification as follows:

## [Gap Category]: [Specific Modification Title]

**Reference:** [Section/Clause of original standard]

**Current Text:** [Text being modified, if applicable]

**Proposed Modification:**
[Provide exact wording of the proposed addition or modification]

**Justification:**
[Explain why this modification is necessary, citing Shariah principles, regulatory requirements, market developments, etc.]

**Implementation Considerations:**
[Provide guidance on practical implementation aspects]

Your modifications must be:
- Shariah-compliant (free from riba, gharar, maysir)
- Technically sound and aligned with accounting principles
- Practical and implementable by Islamic financial institutions
- Clear and unambiguous in language and requirements
"""

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        HumanMessage(content="""
Below are:
1. The key elements extracted from the standard:
{extracted_elements}

2. The identified gaps that need to be addressed:
{identified_gaps}

Based on these inputs, propose specific modifications to address the gaps while maintaining alignment with Islamic finance principles.
""")
    ])

    def modification_logic(inputs):
        """
        Process the extracted elements and identified gaps to suggest specific modifications
        """
        extracted_elements = inputs.get("extracted_elements", "")
        identified_gaps = inputs.get("identified_gaps", "")
        
        # Format the inputs for the LLM
        chain = prompt | llm
        
        # Get modification proposals from the LLM
        response = chain.invoke({"extracted_elements": extracted_elements, "identified_gaps": identified_gaps})
        
        return {"output": response.content}
    
    return RunnableLambda(modification_logic)

## Example usage:
#if __name__ == "__main__":
#    # These would be the outputs from your previous agents
#    extracted_elements = """
#[Key elements extracted from the standard would be here]
#"""
#    
#    identified_gaps = """
#1. **Instruments and Products**:
#   - **Gap**: Emerging financial products such as digital assets and green financing are not covered.
#   - **Importance**: The inclusion of these products would expand the applicability of Istisna'a contracts to modern financial needs.
#   - **Recommendation**: Extend the standard to include guidelines for using Istisna'a in financing digital assets and environmentally sustainable projects.
#    
#[Additional gaps would continue here]
#"""
#    
#    modification_agent = create_modification_agent()
#    result = modification_agent.invoke({
#        "extracted_elements": extracted_elements,
#        "identified_gaps": identified_gaps
#    })
#    
#    print(result["output"])