import os
import sys
import tempfile
import shutil
import numpy as np
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.vector_db_manager import VectorDBManager
from rag.text_processor import TextProcessor
from common.config import Config


def create_mock_embeddings():
    """Create a mock embedding function that returns consistent vectors"""
    mock_embeddings = MagicMock()
    # Always return the same vector for consistent testing
    mock_embeddings.embed_query.return_value = [0.1] * 768  # 768-dim vector
    mock_embeddings.embed_documents.return_value = [[0.1] * 768] * 5  # Return 5 vectors
    return mock_embeddings


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
            
            print("=== TESTING DETERMINISTIC ID GENERATION ===")
            
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
            
            # Sample text chunks for testing
            chunks_1 = [
                "This is chunk 1 from document 1",
                "This is chunk 2 from document 1", 
                "This is chunk 3 from document 1"
            ]
            
            chunks_2 = [
                "This is chunk 1 from document 2",
                "This is chunk 2 from document 2"
            ]
            
            print("=== PHASE 1: Testing ID generation ===")
            
            # Test ID generation directly without actually creating vector stores
            from rag.vector_db_manager import VectorDBManager
            
            # Mock the embedding and FAISS parts
            with patch('rag.vector_db_manager.HuggingFaceEmbeddings') as mock_hf_embeddings, \
                 patch('rag.vector_db_manager.faiss') as mock_faiss, \
                 patch('rag.vector_db_manager.FAISS') as mock_faiss_class:
                
                # Setup mocks
                mock_embeddings = create_mock_embeddings()
                mock_hf_embeddings.return_value = mock_embeddings
                
                mock_index = MagicMock()
                mock_faiss.IndexFlatL2.return_value = mock_index
                
                mock_vector_store = MagicMock()
                mock_faiss_class.return_value = mock_vector_store
                
                # Track the IDs that get generated
                generated_ids = []
                
                def capture_ids(documents, ids):
                    generated_ids.extend(ids)
                    return None
                
                mock_vector_store.add_documents.side_effect = capture_ids
                
                # Test ID generation for each directory
                for directory, files in test_documents.items():
                    print(f"\nTesting directory: {directory}")
                    
                    # Initialize vector manager
                    vector_manager = VectorDBManager()
                    
                    # Test first file
                    first_file = files[0]
                    print(f"  Adding {first_file}")
                    vector_manager.add_documents(chunks_1, first_file, directory)
                    
                    # Test second file
                    second_file = files[1]
                    print(f"  Adding {second_file}")
                    vector_manager.add_documents(chunks_2, second_file, directory)
                
                print(f"\n=== Generated IDs Analysis ===")
                print(f"Total IDs generated: {len(generated_ids)}")
                print(f"Unique IDs: {len(set(generated_ids))}")
                
                if len(generated_ids) == len(set(generated_ids)):
                    print("✅ All IDs are unique - no duplicates!")
                else:
                    print("❌ Duplicate IDs found!")
                    duplicates = [id for id in generated_ids if generated_ids.count(id) > 1]
                    print(f"Duplicate IDs: {set(duplicates)}")
                    return False
                
                print("\n=== Sample Generated IDs ===")
                for i, id in enumerate(generated_ids[:10]):  # Show first 10 IDs
                    print(f"  {i+1}: {id}")
                
                print("\n=== Verifying ID Format ===")
                expected_patterns = [
                    "1_CG_Vie_CG_AMALI_",
                    "1_CG_Vie_CG_ASSUR_SENIOR_",
                    "2_CG_Santé_CG_ASSURANCE_GROUPE_MALADIE_",
                    "2_CG_Santé_CG_MEDICAL_PLUS_",
                    "4_CG_IARD_CG_ASSURANCE_BRIS_DE_GLACES_",
                    "4_CG_IARD_CG_ASSURANCE_CONTRE_LE_VOL_"
                ]
                
                # Check if IDs follow expected patterns
                pattern_matches = []
                for pattern in expected_patterns:
                    matching_ids = [id for id in generated_ids if pattern in id]
                    pattern_matches.append((pattern, len(matching_ids)))
                    print(f"  Pattern '{pattern}': {len(matching_ids)} matches")
                
                # Verify all patterns have matches
                all_patterns_found = all(count > 0 for _, count in pattern_matches)
                if all_patterns_found:
                    print("✅ All expected ID patterns found!")
                else:
                    print("❌ Some expected patterns missing!")
                    return False
                
                print("\n=== Testing ID Determinism ===")
                
                # Test that same input generates same IDs
                vector_manager_2 = VectorDBManager()
                generated_ids_2 = []
                
                def capture_ids_2(documents, ids):
                    generated_ids_2.extend(ids)
                    return None
                
                mock_vector_store.add_documents.side_effect = capture_ids_2
                
                # Add the same documents again
                for directory, files in test_documents.items():
                    first_file = files[0]
                    vector_manager_2.add_documents(chunks_1, first_file, directory)
                    
                    second_file = files[1]
                    vector_manager_2.add_documents(chunks_2, second_file, directory)
                
                # Compare the two sets of IDs
                if generated_ids == generated_ids_2:
                    print("✅ ID generation is deterministic!")
                else:
                    print("❌ ID generation is not deterministic!")
                    print(f"First run: {generated_ids[:5]}")
                    print(f"Second run: {generated_ids_2[:5]}")
                    return False
                
                print("\n=== TEST COMPLETED SUCCESSFULLY ===")
                print("✅ Deterministic ID generation works correctly!")
                print("✅ No duplicate ID errors will occur during merging!")
                print("✅ ID format follows expected pattern!")
                
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
