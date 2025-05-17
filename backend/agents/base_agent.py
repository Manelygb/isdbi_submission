# agents/base_agent.py
import os
import zipfile
import gdown
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

def download_faiss_index():
    file_id = "1AgwRNfoszgiuEremX2166oyBwHvVj2VH"
    output_zip = "index.zip"
    extract_to = "vector_storee"

    if not os.path.exists(os.path.join(extract_to, "index", "index.faiss")):
        print("Downloading FAISS index from Google Drive...")
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, output_zip, quiet=False)

        print("Extracting index.zip...")
        with zipfile.ZipFile(output_zip, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

        os.remove(output_zip)
        print("Index downloaded and extracted.")

def create_agent():
    download_faiss_index()

    # Use correct embedding model (must be real!)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    vector_store = FAISS.load_local(
        "vector_storee/index",
        embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = vector_store.as_retriever()

    # Correct Chat Model usage
    llm = ChatOpenAI(model_name="gpt-3.5-turbo")

    agent = RetrievalQA.from_llm(llm, retriever=retriever)
    return agent

if __name__ == "__main__":
    agent = create_agent()
    while True:
        query = input("Enter your question (or 'exit' to quit): ")
        if query.lower() == "exit":
            break
        response = agent.invoke(query)
        print("\nResponse:\n", response['result'])

