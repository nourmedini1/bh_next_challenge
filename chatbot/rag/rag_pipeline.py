import os
from time import sleep
from common.config import Config
from rag.vector_db_manager import VectorDBManager
from rag.text_processor import TextProcessor
from typing import List, Dict


class RAGPipeline:
    """
    A pipeline to handle the RAG process including text processing and vector database management.
    """

    def __init__(self):
        self.text_processor = TextProcessor()
        self.vector_db_manager = VectorDBManager()

    def __pdf2markdown(self, file_path: str) -> str:
        """
        Convert PDF file to markdown format.

        Args:
            file_path (str): Path to the PDF file.

        Returns:
            str: Markdown content of the PDF.
        """
       #to be implemented
        return ""
    
    def __process_file(self, file_path: str) -> None:
        """
        Process a markdown file and return the text chunks.

        Args:
            file_path (str):  path of the file to process.
        """ 
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")
        else:
            with open(file_path, 'r', encoding='utf-8') as file:
                markdown_content = file.read()
            # Convert markdown to text chunks
            chunks = self.text_processor.split_markdown(markdown_content)
            return chunks

    def initialize_vector_db(self, data_path: str) -> None:    
        """
        Initialize the vector database with text chunks from markdown files.

        Args:
            data_path (str): Path to the directory containing markdown files.
        """
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Data path {data_path} does not exist.")
        
        for root, _, files in os.walk(data_path):
            for file_name in files:
                if file_name.endswith('.md'):
                    file_path = os.path.join(root, file_name)
                    print(f"Processing file: {file_path}")
                    chunks = self.__process_file(file_path)
                    print(f"Number of chunks created: {len(chunks)}")
                    print(f"Adding {len(chunks)} chunks to vector database.")
                    
                    # Use the immediate subdirectory under data_path as folder_name
                    rel_path = os.path.relpath(root, data_path)
                    folder_name = rel_path.split(os.sep)[0] if os.sep in rel_path else rel_path
                    
                    # Pass the directory name to add_documents
                    self.vector_db_manager.add_documents(chunks, file_name, folder_name)
                    self.vector_db_manager.save_VDB(folder_name=folder_name)
