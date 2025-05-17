from langchain_huggingface import HuggingFaceEmbeddings

# Initialize the HuggingFaceEmbeddings.
# You can specify a model name from the Sentence Transformers library
# If no model name is provided, it defaults to 'sentence-transformers/all- impnet-base-v2'
# model_name = "sentence-transformers/all-MiniLM-L6-v2" # A smaller, faster model
model_name = "BAAI/bge-base-en-v1.5" # A commonly used general-purpose model

embeddings = HuggingFaceEmbeddings(model_name=model_name)

# Example documents to embed
documents = [
    "This is the first document.",
    "This document is about the second topic.",
    "And this is the third one, about something else.",
]

# Embed the documents
document_embeddings = embeddings.embed_documents(documents)

print(f"Embeddings for documents (first 10 dimensions of the first document):")
print(document_embeddings[0][:10])
print(f"Number of documents embedded: {len(document_embeddings)}")
print(f"Dimension of embeddings: {len(document_embeddings[0])}")

# Example query to embed
query = "What is the second document about?"

# Embed the query
query_embedding = embeddings.embed_query(query)

print(f"\nEmbedding for query (first 10 dimensions):")
print(query_embedding[:10])
print(f"Dimension of query embedding: {len(query_embedding)}")

# You would typically use these embeddings with a vector store
# For example (requires a vector store library like `chromadb` or `faiss-cpu`):
# from langchain_community.vectorstores import Chroma
# from langchain_community.document_loaders import TextLoader
# from langchain.text_splitter import CharacterTextSplitter
#
# # Load and split the document (using a simple text loader for demonstration)
# # In a real RAG app, you'd load your actual data
# loader = TextLoader("your_document.txt") # Replace with your document path
# documents = loader.load()
# text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
# docs = text_splitter.split_documents(documents)
#
# # Create a vector store from the documents and embeddings
# # This will compute embeddings for each document chunk
# db = Chroma.from_documents(docs, embeddings)
#
# # Perform a similarity search
# query = "Your search query here"
# similar_docs = db.similarity_search(query)
#
# print("\nSimilar documents found:")
# for doc in similar_docs:
#     print(doc.page_content)