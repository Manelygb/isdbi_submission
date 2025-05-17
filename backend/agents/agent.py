from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface_hub import HuggingFaceHub  # Correct import for HuggingFaceHub
from langchain.chains import RetrievalQA

def create_agent():
    # Load the FAISS vector store
    embeddings = HuggingFaceEmbeddings(model_name="intfloat/e5-large-v2")
    vector_store = FAISS.load_local("vector_store/index", embeddings, allow_dangerous_deserialization=True)

    # Use a free Hugging Face chat model
    llm = HuggingFaceHub(
        repo_id="tiiuae/falcon-7b-instruct",
        model_kwargs={"temperature": 0.7, "max_length": 512}
    )

    retriever = vector_store.as_retriever()
    
    # Use from_chain_type instead of from_llm and specify the llm parameter
    agent = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever
    )
    
    return agent