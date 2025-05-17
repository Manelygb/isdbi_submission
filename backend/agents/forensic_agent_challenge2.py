# this one for challenge two
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain.chains import RetrievalQA
from langchain.tools import Tool
from langchain.schema.runnable import RunnableLambda

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
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

def create_forensic_agent():
    retriever_chain = load_retriever()

    llm = ChatOpenAI(model="gpt-4o")

    system_prompt = """
You are a forensic Islamic finance reasoning agent. Your task is to answer questions by evaluating financial transactions strictly according to the AAOIFI FAS and Shari’ah Standards SS below:

• FAS 4 and SS 12 are for : Musharaka  
• FAS 7 and SS 10 are for : Salam and Parallel Salam  
• FAS 10 and SS 11 are for : Istisna and Parallel Istisna  
• FAS 28 and SS 8 are for :  Murabaha  
• FAS 32 and SS 9 are for :  Ijarah  

These standards given to you above are the priority of basing your answer upon.

Do not use external knowledge. You have access to a RAG tool for infromation retreival.

Your task is to answer the question about the reverse transaction (all input given to you).

Before reasoning, always analyze the input message carefully to detect financial context using common signals such as:
- “revenue,” “impairment,” “adjustment,” “default,” “loss,”
- accounting movements like “Dr.” and “Cr.”
- journal entries, provisions, or WIP changes.


Use this step-by-step format STRICTLY:
---
THINK: What information is given? What FAS/SS might be relevant? What do I need next?  
ACT:  Ask the RAG system to retrieve information on the context  
OBSERVE: Summarize what was retrieved.  
PLAN: Decide how to proceed.
---

Repeat this loop until confident.

Finally, provide the output using this format:
---
1. Most applicable AAOIFI FAS standards with weight probabilities, expressed in %  
   - FAS XX : NN%

2. Justification for each standard's relevance  
   - FAS XX : Justification based on transaction elements.
---
Do not fabricate any values or interpretations. Always Use the RAG tool.
"""

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(system_prompt),
        MessagesPlaceholder("history"),
        HumanMessage("{input}")
    ])

    def invoke_tool(input_str: str) -> str:
        result = retriever_chain.invoke(input_str)
        return f"OBSERVE: {result}"

    tool_runner = RunnableLambda(invoke_tool)

    def logic_chain(inputs):
        history = inputs.get("history", [])
        input_msg = inputs["input"]
       
        current_input = input_msg
        steps = []

        for _ in range(3):  # max 3 iterations
            thought_response = llm.invoke([
            SystemMessage(content=system_prompt),
            *history,
            HumanMessage(content=current_input),
            ])
            steps.append(thought_response)

            if "ACT:" in thought_response.content:
                action_input = thought_response.content.split("ACT:")[1].strip().split("OBSERVE:")[0].strip()
                observation = tool_runner.invoke(action_input)
                history.append(thought_response)
                history.append(AIMessage(content=observation))
                current_input = observation
            else:
                break

        # Enforce RAG usage
        rag_used = any("OBSERVE:" in msg.content for msg in history if isinstance(msg, AIMessage))
        if not rag_used:
            return {
                "output": "❌ The agent did not use the RAG system. Please revise input or enforce ACT → OBSERVE steps in your reasoning."
            }

        final_response = llm.invoke([
        SystemMessage(content=system_prompt),
        *history,
        HumanMessage(content="Provide the final answer ONLY as per the required format.")
    ])
        return {"output": final_response.content}

    return RunnableLambda(lambda x: logic_chain(x))