import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from translatepy import Translator
from langchain_core.documents import Document


load_dotenv()

# TODO: try this tomorrow: Linq-AI-Research/Linq-Embed-Mistral

def build_vector_store(data_dir="../../data/raw", model_name="BAAI/bge-base-en-v1.5"):
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Directory '{data_dir}' not found.")

    all_documents = []
    translator = Translator()

    for filename in os.listdir(data_dir):
        if filename.lower().endswith(".pdf"):
            path = os.path.join(data_dir, filename)
            loader = PyPDFLoader(path)
            loaded_pages = loader.load()
            
            if loaded_pages:
                print(f"⏳ Translating {len(loaded_pages)} pages from {filename}...")
                translated_pages = []
                for i, page_doc in enumerate(loaded_pages):
                    try:
                        translated_text = translator.translate(page_doc.page_content, "fr", "en").result
                        page_doc.page_content = translated_text
                        page_doc.metadata["language"] = "en"
                        translated_pages.append(page_doc)
                        if (i + 1) % 10 == 0:
                             print(f"    Translated {i+1}/{len(loaded_pages)} pages from {filename}")
                    except Exception as e:
                        print(f"⚠️ Error translating page {page_doc.metadata.get('page', i)} of {filename}: {e}")
                        continue
                all_documents.extend(translated_pages)
                print(f"✅ Loaded and translated {len(translated_pages)} docs from {filename}")

    if not all_documents:
        raise ValueError("No PDF documents were loaded or translated successfully.")

    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = text_splitter.split_documents(all_documents)

    if not chunks:
        raise ValueError("Document splitting produced no chunks. Check PDF contents and translation results.")

    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    vector_store = FAISS.from_documents(chunks, embeddings)

    save_path_dir = "../../vector_storee/law_docs_hf"
    os.makedirs(os.path.dirname(save_path_dir), exist_ok=True)
    
    vector_store.save_local(save_path_dir)
    print(f"🎉 Vector store built and saved successfully to {save_path_dir}.")

if __name__ == "__main__":
    build_vector_store()