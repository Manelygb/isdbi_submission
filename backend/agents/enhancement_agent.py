# second of challenge 3
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()

def create_enhancement_agent():
    """
    Creates an agent responsible for identifying areas to enhance in Islamic finance standards
    based on the key elements extracted by the extractive agent.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0.4)

    system_prompt = """
You are a specialized Islamic Finance Standards Enhancement Agent. Your task is to identify gaps, inconsistencies, 
and areas for improvement in AAOIFI standards based on extracted key elements.

Analyze the extracted elements and identify enhancement opportunities in the following categories:

1. **Instruments and Products**: Identify emerging financial products not covered by the standard.

2. **Transaction Structures**: Evaluate if current structures reflect market needs, including digital transactions or smart contracts.

3. **Risk Mitigation**: Identify emerging methods or technologies (e.g., blockchain-based risk solutions) not covered.

4. **Compliance Requirements**: Note newer regulatory changes (e.g., IFRS updates, Basel III compliance) that should be included.

5. **Legal Framework**: Identify new legal frameworks that should be addressed (e.g., digital asset regulations, cross-border regulations).

6. **Regulatory Compliance**: Identify gaps due to recent legal changes.

7. **Market Developments**: Note recent market trends not covered (e.g., digital assets, crowdfunding, Sukuk markets).

8. **Technological Innovations**: Evaluate if the standard considers emerging technologies like blockchain, AI, or smart contracts.

9. **Scalability and Adaptability**: Assess if the standard is adaptable to changing market conditions.

10. **Shariah Guidelines**: Identify new Shariah rulings or updates not addressed.

11. **Ethical Considerations**: Note gaps in how ethical concerns are addressed.

12. **Operational Guidelines**: Identify gaps in application, particularly for new sectors or innovations.

13. **Monitoring and Evaluation**: Suggest new methods or tools for assessment.

14. **Clarity and Terminology**: Recommend improvements in definitions, processes, accounting treatments, or terminology.

For each category where you identify a gap or enhancement opportunity:
1. Clearly state the gap or limitation
2. Explain why it matters in the current Islamic finance landscape
3. Provide a specific recommendation for enhancement

If a category appears adequately addressed in the standard based on the extracted elements, indicate this with "No significant gaps identified" and explain why current coverage is sufficient.

Your response should be detailed, practical, and directly applicable to enhancing the standard.
"""

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        HumanMessage(content="{extracted_elements}")
    ])

    def enhancement_logic(inputs):
        """
        Process the extracted elements and identify enhancement opportunities
        """
        extracted_elements = inputs["extracted_elements"]
        
        # Format the input for the LLM
        formatted_input = f"Based on the following key elements extracted from the standard, identify enhancement opportunities:\n\n{extracted_elements}"
        
        # Create messages for the LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=formatted_input)
        ]
        
        # Get enhancement recommendations from the LLM
        response = llm.invoke(messages)
        
        return {"output": response.content}
    
    return RunnableLambda(enhancement_logic)