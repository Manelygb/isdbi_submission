# first of challenge 3
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableLambda
from agents.base_agent import download_faiss_index
import time

def load_retriever():
    #download_faiss_index()
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = FAISS.load_local(
        "vector_storee/index",
        embeddings,
        allow_dangerous_deserialization=True
    )
    retriever = vector_store.as_retriever()
    return RetrievalQA.from_chain_type(llm=ChatOpenAI(model="gpt-4o"), retriever=retriever)


def create_extractive_agent():
    retriever_chain = load_retriever()
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

    system_prompt = """
Extract the key elements that allows for gap analysis, by answering the following questions:
**Objective of the Standard**: What is the primary purpose of the standard? How does it align with the broader goals of the organization or industry?
**Scope of the Standard**: What does the standard cover? What financial instruments, transactions, or practices are addressed?
**Target Audience**: Who are the intended users of the standard? Are there any specific industries, regions, or types of financial entities that this standard targets?
**Instruments and Products**: What specific financial instruments or products are defined in the standard (e.g., loans, investments, contracts)?
**Transaction Structures**: What transaction structures are outlined in the standard (e.g., fixed-rate contracts, profit-sharing models)
**Risk Mitigation**: How does the standard address risk mitigation (e.g., hedging, diversification, shared risk models)?
**Compliance Requirements**: What are the compliance requirements mentioned (e.g., **Shariah compliance**, **local regulatory frameworks**)?
**Governance and Audits**: How does the standard incorporate governance principles or auditing mechanisms (e.g., **Shariah board approvals**, **audit trails**)?
**Legal Framework**: What legal aspects are considered in the standard (e.g., **contract law**, **tax law**)?
**Regulatory Compliance**: How does the standard comply with international or local regulations (e.g., **AML**, **KYC**, **data privacy laws**)?
**Ethical Considerations**: Does the standard address ethical financial practices in line with Shariah law (e.g., **avoiding gharar**, **ensuring fairness**)?
**Operational Guidelines**: What practical steps does the standard outline for implementation (e.g., **contract management**, **risk assessments**, **reporting requirements**)?
**Monitoring and Evaluation**: How does the standard propose monitoring or evaluating its effectiveness?

Do not fabricate details. If the information is not found in the documents, state "Not specified".

The output format:
category of question: answer to the question.
"""

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        MessagesPlaceholder(variable_name="history"),
        HumanMessage(content="{input}")
    ])
    
    def extraction_logic(inputs):
        input_query = inputs["input"]
        history = inputs.get("history", [])

        # Get relevant content from the retriever chain
        query_result = retriever_chain.invoke(input_query)
        #print("Query result:", query_result)  # good for debugging
        
        # Prepare the formatted input with the query result
        formatted_input = f"{input_query}\n\nRelevant standard content:\n{query_result['result']}"
        
        # Create the messages list directly
        messages = [
            SystemMessage(content=system_prompt),
            # Add history messages if any
            *history,
            HumanMessage(content=formatted_input)
        ]

        # Invoke the LLM with the messages
        response = llm.invoke(messages)
        print("LLM response: \n", response.content)
        
        return {"output": response.content}
    
    return RunnableLambda(extraction_logic)