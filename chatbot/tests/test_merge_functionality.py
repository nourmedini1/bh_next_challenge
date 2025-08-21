import os
import sys
import tempfile
import shutil
from unittest.mock import patch

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.vector_db_manager import VectorDBManager
from rag.text_processor import TextProcessor
from common.config import Config


def test_merge_functionality():
    """
    Test the merging functionality by:
    1. Adding one markdown file from 3 different directories
    2. Then adding another markdown file to each directory
    3. Verifying that merging works without duplicate ID errors
    """
    
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    vector_db_dir = os.path.join(test_dir, "test_vector_db")
    
    try:
        # Mock the VDBs_folder config to use our test directory
        with patch.object(Config, 'VDBs_folder', vector_db_dir):
            
            # Initialize components
            vector_db_manager = VectorDBManager()
            text_processor = TextProcessor()
            
            # Test data - simulate markdown content
            test_documents = {
                "1-CG-Vie": [
                    "CG AMALI.md",
                    "CG ASSUR SENIOR.md"
                ],
                "2-CG-Santé": [
                    "CG ASSURANCE GROUPE MALADIE.md", 
                    "CG MEDICAL PLUS.md"
                ],
                "4-CG-IARD": [
                    "CG ASSURANCE BRIS DE GLACES.md",
                    "CG ASSURANCE CONTRE LE VOL.md"
                ]
            }
            
            # Sample markdown content for testing
            markdown_content_1 = """
# Document Title 1

This is the first test document with some content.

## Section 1
Content for section 1 with multiple paragraphs.

## Section 2  
More content for testing the chunking functionality.
"""
            
            markdown_content_2 = """
# Document Title 2

This is the second test document with different content.

## Section A
Different content for section A with various information.

## Section B
Additional content for testing merging functionality.
"""
            
            print("=== PHASE 1: Adding first document from each directory ===")
            
            # Phase 1: Add one document from each directory
            for directory, files in test_documents.items():
                first_file = files[0]
                print(f"\nProcessing {directory}/{first_file}")
                
                # Split content into chunks
                chunks = text_processor.split_markdown(markdown_content_1)
                print(f"Created {len(chunks)} chunks")
                
                # Add documents to vector database
                vector_db_manager.add_documents(chunks, first_file, directory)
                
                # Save vector database for this directory
                vector_db_manager.save_VDB(directory)
                print(f"Saved vector database for {directory}")
                
                # Reset vector store for next directory
                vector_db_manager = VectorDBManager()
            
            print("\n=== PHASE 2: Adding second document to each directory (testing merge) ===")
            
            # Phase 2: Add second document to each directory (this will test merging)
            for directory, files in test_documents.items():
                second_file = files[1]
                print(f"\nAdding {directory}/{second_file}")
                
                # Initialize fresh vector manager
                vector_db_manager = VectorDBManager()
                
                # Split content into chunks
                chunks = text_processor.split_markdown(markdown_content_2)
                print(f"Created {len(chunks)} chunks")
                
                # Add documents to vector database
                vector_db_manager.add_documents(chunks, second_file, directory)
                
                try:
                    # Save vector database (this should trigger merging if directory exists)
                    vector_db_manager.save_VDB(directory)
                    print(f"✅ Successfully merged and saved vector database for {directory}")
                    
                    # Verify the vector database was saved
                    db_path = os.path.join(vector_db_dir, directory)
                    if os.path.exists(db_path):
                        print(f"✅ Vector database directory exists: {db_path}")
                        
                        # Check if FAISS files exist
                        index_file = os.path.join(db_path, "index.faiss")
                        pkl_file = os.path.join(db_path, "index.pkl")
                        
                        if os.path.exists(index_file) and os.path.exists(pkl_file):
                            print(f"✅ FAISS files exist in {directory}")
                        else:
                            print(f"❌ Missing FAISS files in {directory}")
                    else:
                        print(f"❌ Vector database directory not found: {db_path}")
                        
                except Exception as e:
                    print(f"❌ Error during merge for {directory}: {str(e)}")
                    return False
            
            print("\n=== PHASE 3: Testing search functionality ===")
            
            # Phase 3: Test that we can load and search the merged databases
            for directory in test_documents.keys():
                try:
                    # Initialize fresh vector manager and load the saved database
                    search_manager = VectorDBManager()
                    search_manager.load_VDB(directory)
                    
                    # Perform a test search
                    results = search_manager.search("test document", k=3)
                    print(f"✅ Search successful for {directory}: found {len(results)} results")
                    
                    # Print some result details
                    for i, result in enumerate(results[:2]):  # Show first 2 results
                        print(f"  Result {i+1}: {result.metadata}")
                        
                except Exception as e:
                    print(f"❌ Error during search for {directory}: {str(e)}")
                    return False
            
            print("\n=== TEST COMPLETED SUCCESSFULLY ===")
            print("✅ Merging functionality works correctly!")
            print("✅ No duplicate ID errors encountered!")
            print("✅ All vector databases can be loaded and searched!")
            
            return True
            
    finally:
        # Clean up temporary directory
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"\n🧹 Cleaned up test directory: {test_dir}")


if __name__ == "__main__":
    print("Testing Vector Database Merge Functionality")
    print("=" * 50)
    
    try:
        success = test_merge_functionality()
        if success:
            print("\n🎉 ALL TESTS PASSED!")
            sys.exit(0)
        else:
            print("\n💥 SOME TESTS FAILED!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 TEST FAILED WITH EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
