
import os
from typing import List, Dict
import faiss

from langchain_core.documents import Document
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from common.config import Config


                    
class VectorDBManager:
    """
    Manages FAISS vector store with embeddings and metadata.
    """

    def __init__(self):
        # Load embedding model name from config
        self.model_name = Config().model_name  

        # Initialize embedding function
        print(f"Using embedding model: {self.model_name}")
        self.embeddings = HuggingFaceEmbeddings(model_name=self.model_name)

        # Initialize FAISS index
        dim = len(self.embeddings.embed_query("hello world"))
        index = faiss.IndexFlatL2(dim)

        #distance strategy
        self.distance_strategy = Config().distance_strategy

        # Initialize vector store
        self.vector_store = FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
            distance_strategy=self.distance_strategy,
        )
    
    
    def __create_documents(self, chunks: List[str], file_name: str, directory_name: str) -> List[Document]:
        """        Create Document objects from text chunks with metadata.

        Args:
            chunks (List[str]): List of text chunks.
            file_name (str): Name of the file from which chunks are derived.
            directory_name (str): Name of the directory containing the file.

        Returns:
            List[Document]: List of Document objects.
        """
        documents = []
        for chunk in chunks:
            metadata = {
                "file_name": file_name,
                "directory_name": directory_name,
            }
            documents.append(Document(page_content=chunk, metadata=metadata))
        return documents

    
    def add_documents(self, chunks: List[str], file_name: str, directory_name: str) -> None:
        """
        Add documents to the vector store.

        Args:
            chunks (List[str]): List of text chunks.
            file_name (str): Name of the file from which chunks are derived.
            directory_name (str): Name of the directory containing the file.
        """
        documents = self.__create_documents(chunks, file_name, directory_name)
        
        # Generate deterministic IDs: directory_filename_chunknumber
        # Remove file extension and clean up names for ID generation
        clean_filename = os.path.splitext(file_name)[0]  # Remove .md extension
        clean_directory = directory_name.replace("/", "_").replace("\\", "_")  # Handle path separators
        clean_filename = clean_filename.replace(" ", "_").replace("-", "_")  # Replace spaces and hyphens
        
        ids = []
        for i in range(len(documents)):
            chunk_id = f"{clean_directory}_{clean_filename}_{i+1}"
            ids.append(chunk_id)
        
        # Check if existing vector store exists and load it
        path = f"{Config().VDBs_folder}/{directory_name}"
        if os.path.exists(path):
            try:
                # Load existing vector store to replace current empty one
                self.vector_store = FAISS.load_local(path, self.embeddings, distance_strategy=self.distance_strategy, allow_dangerous_deserialization=True)
                print(f"Loaded existing vector store from {path}")
            except Exception as e:
                print(f"Warning: Could not load existing vector store: {e}")
                print("Continuing with empty vector store...")
        
        # Check which documents already exist
        existing_ids = set(self.vector_store.index_to_docstore_id.values())
        new_documents = []
        new_ids = []
        
        for doc, doc_id in zip(documents, ids):
            if doc_id not in existing_ids:
                new_documents.append(doc)
                new_ids.append(doc_id)
            else:
                print(f"Skipping duplicate document with ID: {doc_id}")
        
        if new_documents:
            self.vector_store.add_documents(new_documents, ids=new_ids)
            print(f"Added {len(new_documents)} new documents (skipped {len(documents) - len(new_documents)} duplicates)")
        else:
            print("No new documents to add - all documents already exist")
        
    
    def search(self, query: str, k: int = 5) -> List[Document]:
        """
        Search for documents similar to the query and return top k results with related metadata and relevance scores.

        Args:
            query (str): The search query.
            k (int): Number of top results to return.
        Returns:
            List[Document]: List of Document objects with metadata and relevance scores.
        """
        results = self.vector_store.similarity_search_with_score(query, k=k)
        return [Document(page_content=res[0].page_content, metadata=res[0].metadata, score=res[1]) for res in results]  
    
    def save_VDB(self, folder_name: str) -> None:
        """
        Save the vector database to a specified path.

        Args:
            folder_name (str): Name of the folder to save the vector database.
        """
        path = f"{Config().VDBs_folder}/{folder_name}"

        # Create directory if it doesn't exist
        if not os.path.exists(path):
            os.makedirs(path)
        
        # Simply save the current vector store (merging was already done in add_documents)
        self.vector_store.save_local(path)
    
    def load_VDB(self, folder_name: str) -> None:
        """
        Load the vector database from a specified path.

        Args:
            folder_name (str): Name of the folder containing the vector database.
        """
        path = f"{Config().VDBs_folder}/{folder_name}"
        self.vector_store = FAISS.load_local(path, self.embeddings, distance_strategy=self.distance_strategy, allow_dangerous_deserialization=True)
        

    
    