# agent two of challenge four
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.vectorstores import FAISS
from agents.base_agent import download_faiss_index
import re


def load_retriever():
    download_faiss_index()
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = FAISS.load_local(
        "vector_storee/index",
        embeddings,
        allow_dangerous_deserialization=True
    )
    retriever = vector_store.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(llm=ChatOpenAI(model_name="gpt-4o"), retriever=retriever)
    return qa_chain


def create_evaluate_situation_agent():
    retriever_chain = load_retriever()
    llm = ChatOpenAI(model="gpt-4o")

    # Updated system prompt with explicit primary contract identification
    system_prompt = """
You are a Shariah-compliant forensic Islamic finance advisor analyzing financial transactions using ONLY the AAOIFI FAS and Shari'ah Standards listed below:

• FAS 4 + SS 12: Musharaka
• FAS 7 + SS 10: Salam and Parallel Salam  
• FAS 10 + SS 11: Istisna and Parallel Istisna
• FAS 28 + SS 8: Murabaha
• FAS 32 + SS 9: Ijarah

Do NOT use your general knowledge about Islamic finance. If you need information about these standards, use the available RAG tool to retrieve it.

## Evaluation Process:
1. Identify the key elements of the transaction/project (type, parties, assets, financial structure)
2. Determine which Islamic contract structures might apply
3. Retrieve specific information about the relevant standards using the RAG tool
4. Analyze compliance with AAOIFI standards and evaluate financial viability
5. Make a recommendation with justification

## Output Format:
```
ANALYSIS:
- Transaction Type: [Description]
- Key Parties: [List]
- Assets/Services: [Description]
- Financial Structure: [Description]
- Relevant Shariah Considerations: [List]

APPLICABLE STANDARDS:
- FAS XX / SS YY: [Weight]%
- [Additional standards if applicable]

Note: Weights must sum to 100%

PRIMARY RECOMMENDED CONTRACT: [Specify the single most appropriate contract type]

COMPLIANCE SCORE: [0-2]
(2 = fully compliant and optimal, 1 = acceptable with reservations, 0 = non-compliant)

RECOMMENDATION: [Proceed/Proceed with modifications/Do not proceed]

JUSTIFICATION:
- FAS XX / SS YY: [Explanation of relevance and compliance]
- [Justifications for additional standards if applicable]

RISK EVALUATION:
- [Key Shariah compliance risks]
- [Mitigation strategies]

IMPLEMENTATION CONSIDERATIONS:
- [Key points to ensure Shari'ah compliance]
```

Always include a clear "PRIMARY RECOMMENDED CONTRACT" section that specifies the single most appropriate Islamic contract structure (e.g., "Murabaha", "Ijarah", "Istisna'a", "Musharaka", or "Salam") for this situation. This should be the contract with the highest percentage weight.
"""

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        HumanMessage(content="{input}")
    ])

    def process_query(input_str: str) -> dict:
        # First, extract necessary information about the transaction/project
        situation_prompt = f"""
        Analyze this financial situation:
        
        {input_str}
        
        What specific information from AAOIFI standards do you need to properly evaluate this case?
        """
        
        initial_analysis = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=situation_prompt)
        ])
        
        # Identify which standards might be relevant based on initial analysis
        standards_needed = initial_analysis.content
        
        # Retrieve information about relevant standards
        standards_info = retriever_chain.invoke(standards_needed)
        
        # Generate the final analysis with retrieved information
        final_prompt = f"""
        Based on the following financial situation:
        
        {input_str}
        
        And these relevant AAOIFI standards:
        
        {standards_info}
        
        Provide your complete analysis and recommendation in the required output format. 
        Be sure to clearly indicate the PRIMARY RECOMMENDED CONTRACT.
        """
        
        final_response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=final_prompt)
        ])
        
        evaluation_results = final_response.content
        
        # Extract the primary recommended contract
        primary_contract = None
        
        # Method 1: Look for the explicit PRIMARY RECOMMENDED CONTRACT section
        primary_contract_match = re.search(r"PRIMARY RECOMMENDED CONTRACT:\s*(.*?)(?:\n|$)", evaluation_results)
        if primary_contract_match:
            primary_contract = primary_contract_match.group(1).strip()
        
        # Method 2: If not found, use the highest weighted contract from APPLICABLE STANDARDS
        if not primary_contract and "APPLICABLE STANDARDS:" in evaluation_results:
            standards_section = evaluation_results.split("APPLICABLE STANDARDS:")[1].split("\n\n")[0]
            standards_lines = standards_section.strip().split("\n")
            
            highest_weight = 0
            for line in standards_lines:
                if "%" in line:
                    parts = line.split(":")
                    if len(parts) >= 2:
                        standard = parts[0].strip()
                        # Extract FAS/SS number for contract type identification
                        if "FAS" in standard and "SS" in standard:
                            for contract_type in ["Musharaka", "Salam", "Istisna", "Murabaha", "Ijarah"]:
                                if contract_type.lower() in standard.lower():
                                    contract_name = contract_type
                                    break
                            else:
                                contract_name = standard
                                
                            weight_str = parts[1].strip().replace("%", "")
                            try:
                                weight = float(weight_str)
                                if weight > highest_weight:
                                    highest_weight = weight
                                    primary_contract = contract_name
                            except ValueError:
                                continue
        
        # If still not found, use a default based on any keyword matches
        if not primary_contract:
            for contract_type in ["Musharaka", "Salam", "Istisna", "Murabaha", "Ijarah"]:
                if contract_type.lower() in evaluation_results.lower():
                    primary_contract = contract_type
                    break
            else:
                primary_contract = "Unknown"  # Fallback
        
        return {
            "output": evaluation_results,
            "primary_contract": primary_contract,
            "evaluation_results": evaluation_results
        }

    # Create the main chain
    chain = RunnableLambda(process_query)
    
    return chain