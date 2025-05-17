# third of challenge 4
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.vectorstores import FAISS
from agents.base_agent import download_faiss_index


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


def create_contract_drafting_agent():
    retriever_chain = load_retriever()
    llm = ChatOpenAI(model="gpt-4o")

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

## Output Format:
```
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
```

## Guidelines:
- Use formal, precise language like official Islamic financing documentation
- Include only information present in the inputs—do not invent specific dates, client names, or exact values not provided
- Explicitly reference relevant AAOIFI standards in your explanations
- Ensure the scenario is logically coherent and complies with all Shariah principles
- Address potential issues identified in the financial assessment
- Describe how any risks or compliance concerns will be mitigated
- Focus on the practical implementation details a bank would need to follow
"""

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        HumanMessage(content="{input}")
    ])

    def process_query(input_data: dict) -> str:
        # Extract project description, evaluation results, and primary contract
        project_description = input_data.get("project_description", "")
        evaluation_results = input_data.get("evaluation_results", "")
        
        # Use the explicitly provided primary contract if available
        primary_contract = input_data.get("primary_contract", "Unknown")
        
        # Retrieve specific contract information from the knowledge base
        contract_info_query = f"What are the key requirements, structure, and implementation details for {primary_contract} according to AAOIFI standards?"
        contract_info = retriever_chain.invoke(contract_info_query)
        
        # Construct the input for the LLM
        contract_prompt = f"""
        Please create a detailed Islamic financing scenario based on:

        PROJECT DESCRIPTION:
        {project_description}

        RECOMMENDED CONTRACT TYPE:
        {primary_contract}

        EVALUATION RESULTS:
        {evaluation_results}

        ADDITIONAL CONTRACT INFORMATION:
        {contract_info}

        Create a professional, Shariah-compliant financing scenario following the required output format.
        """
        
        # Generate the contract scenario
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=contract_prompt)
        ])
        
        return response.content

    # Create the main chain
    chain = RunnableLambda(lambda x: {"output": process_query(x)})
    
    return chain