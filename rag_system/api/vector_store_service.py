"""
Vector store management service for loading and querying vector stores.
"""

import os
from typing import Dict, List, Optional
from vector_stores_creation.vector_db_manager import VectorDBManager
from common.config import Config
from api.config import VECTOR_STORE_CONFIG, get_all_store_names
from api.models import DocumentResult


class VectorStoreService:
    """Service class for managing vector stores."""
    
    def __init__(self):
        self.vector_stores: Dict[str, VectorDBManager] = {}
        self.config = Config()
    
    async def load_all_vector_stores(self) -> Dict[str, bool]:
        """
        Load all vector stores on startup for performance optimization.
        
        Returns:
            Dict[str, bool]: Dictionary mapping store names to load success status
        """
        print("Loading vector stores on startup...")
        load_results = {}
        
        for store_name in get_all_store_names():
            success = await self.load_vector_store(store_name)
            load_results[store_name] = success
            
        print(f"Loaded {len(self.vector_stores)} vector stores successfully!")
        return load_results
    
    async def load_vector_store(self, store_name: str) -> bool:
        """
        Load a specific vector store.
        
        Args:
            store_name: Name of the vector store to load
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            store_config = VECTOR_STORE_CONFIG.get(store_name)
            if not store_config:
                print(f"Warning: Unknown vector store {store_name}")
                return False
                
            print(f"Loading {store_name} - {store_config['name']}...")
            
            # Check if vector store exists
            store_path = f"{self.config.VDBs_folder}/{store_name}"
            if not os.path.exists(store_path):
                print(f"Warning: Vector store {store_name} not found at {store_path}")
                return False
                
            # Initialize and load vector store
            vm = VectorDBManager()
            vm.load_VDB(store_name)
            self.vector_stores[store_name] = vm
            
            print(f"Successfully loaded {store_name}")
            return True
            
        except Exception as e:
            print(f"Failed to load {store_name}: {str(e)}")
            return False
    
    def is_store_loaded(self, store_name: str) -> bool:
        """Check if a vector store is loaded."""
        return store_name in self.vector_stores
    
    def get_loaded_stores(self) -> List[str]:
        """Get list of loaded vector store names."""
        return list(self.vector_stores.keys())
    
    async def query_vector_store(self, store_name: str, query: str, k: int = 5) -> List[DocumentResult]:
        """
        Query a specific vector store.
        
        Args:
            store_name: Name of the vector store to query
            query: Search query
            k: Number of results to return
            
        Returns:
            List[DocumentResult]: List of search results
            
        Raises:
            ValueError: If vector store is not loaded
            Exception: If query fails
        """
        if store_name not in self.vector_stores:
            raise ValueError(f"Vector store '{store_name}' not loaded or not found")
        
        try:
            # Query the vector store
            vm = self.vector_stores[store_name]
            results = vm.search(query, k=k)
            
            # Convert results to DocumentResult format
            document_results = []
            for doc in results:
                doc_result = DocumentResult(
                    content=doc.page_content,
                    metadata=doc.metadata,
                    score=getattr(doc, 'score', None)
                )
                document_results.append(doc_result)
            
            return document_results
            
        except Exception as e:
            raise Exception(f"Error querying vector store '{store_name}': {str(e)}")
    
    def get_store_stats(self) -> Dict[str, int]:
        """Get statistics about loaded vector stores."""
        return {
            "loaded_stores": len(self.vector_stores),
            "total_stores": len(VECTOR_STORE_CONFIG)
        }

    async def add_document_to_store(self, store_name: str, markdown_content: str, file_name: str) -> int:
        """
        Add a markdown document to a specific vector store.
        
        Args:
            store_name: Name of the vector store to add to
            markdown_content: Content of the markdown file
            file_name: Name of the file
            
        Returns:
            int: Number of chunks added
            
        Raises:
            Exception: If store doesn't exist or isn't loaded
        """
        # Validate store exists and is loaded
        if store_name not in VECTOR_STORE_CONFIG:
            raise Exception(f"Vector store '{store_name}' does not exist")
            
        if store_name not in self.vector_stores:
            raise Exception(f"Vector store '{store_name}' is not loaded")
        
        # Import text processor
        from vector_stores_creation.text_processor import TextProcessor
        
        # Process the markdown content into chunks
        text_processor = TextProcessor()
        chunks = text_processor.split_markdown(markdown_content)
        
        if not chunks:
            raise Exception("No valid chunks could be extracted from the markdown content")
        
        # Get the vector store manager
        vm = self.vector_stores[store_name]
        
        # Add documents to the vector store
        vm.add_documents(chunks, file_name, store_name)
        
        # Save the updated vector store
        vm.save_VDB(store_name)
        
        return len(chunks)
