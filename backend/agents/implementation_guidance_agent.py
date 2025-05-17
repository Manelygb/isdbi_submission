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


def create_implementation_guidance_agent():
    retriever_chain = load_retriever()
    llm = ChatOpenAI(model="gpt-4o")

    system_prompt = """
You are an expert Islamic finance implementation advisor specializing in practical execution of Shariah-compliant contracts.

## Your Task:
Create a comprehensive implementation checklist and guidance document for financial institutions to correctly execute the proposed Islamic financing structure.

## Input Information:
1. Project description (purpose, costs, parties involved)
2. Primary Islamic contract type (e.g., Murabaha, Ijarah, Istisna'a, Musharaka, Salam)
3. Detailed contract structure and scenario from the previous agent
4. Full financial and Shariah compliance assessment

## Output Requirements:
Produce practical, actionable guidance that:
- Lists all required documentation and legal agreements
- Provides step-by-step implementation instructions
- Identifies critical control points to ensure Shariah compliance
- Includes a timeline with key milestones
- Addresses potential operational and Shariah compliance risks
- Specifies accounting and reporting requirements per AAOIFI standards

## Output Format:
```
# IMPLEMENTATION GUIDANCE: [CONTRACT TYPE]

## DOCUMENTATION REQUIREMENTS
[Comprehensive list of all required documents, forms, and legal agreements]

## PRE-EXECUTION CHECKLIST
[List of items that must be verified before contract execution]

## IMPLEMENTATION TIMELINE
[Step-by-step implementation process with key milestones]

## CRITICAL SHARIAH CONTROL POINTS
[Specific points in the process where Shariah compliance must be verified]

## OPERATIONAL GUIDELINES
[Practical advice for operations teams on executing each stage]

## ACCOUNTING TREATMENT
[Guidance on accounting entries according to AAOIFI standards]

## SHARIAH AUDIT REQUIREMENTS
[Requirements for ongoing Shariah auditing and compliance]

## RISK MITIGATION MEASURES
[Specific measures to address identified risks]

## KEY PERFORMANCE INDICATORS
[Metrics to monitor success and compliance]
```

## Guidelines:
- Be extremely practical and operational in your guidance
- Include detailed checklists that bank staff can use directly
- Reference specific AAOIFI accounting and Shariah standards for each recommendation
- Focus on preventing common mistakes and ensuring Shariah compliance throughout
- Provide clear templates or examples where appropriate
- Consider both financial institution and client perspectives
- Address both initial implementation and ongoing management
- Ensure all guidance aligns with AAOIFI standards and best practices
"""

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        HumanMessage(content="{input}")
    ])

    def process_query(input_data: dict) -> str:
        # Extract relevant information from input
        project_description = input_data.get("project_description", "")
        evaluation_results = input_data.get("evaluation_results", "")
        contract_scenario = input_data.get("contract_scenario", "")
        
        # Use the explicitly provided primary contract
        primary_contract = input_data.get("primary_contract", "Unknown")
        
        # Retrieve implementation best practices from the knowledge base
        implementation_query = f"What are the implementation requirements, accounting treatment, and audit guidelines for {primary_contract} according to AAOIFI standards?"
        implementation_info = retriever_chain.invoke(implementation_query)
        
        # Construct the input for the LLM
        implementation_prompt = f"""
        Please create detailed implementation guidance based on:

        PROJECT DESCRIPTION:
        {project_description}

        CONTRACT TYPE:
        {primary_contract}

        CONTRACT SCENARIO:
        {contract_scenario}

        EVALUATION RESULTS:
        {evaluation_results}

        ADDITIONAL IMPLEMENTATION INFORMATION:
        {implementation_info}

        Create comprehensive, practical implementation guidance following the required output format.
        """
        
        # Generate the implementation guidance
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=implementation_prompt)
        ])
        
        return response.content

    # Create the main chain
    chain = RunnableLambda(lambda x: {"output": process_query(x)})
    
    return chain