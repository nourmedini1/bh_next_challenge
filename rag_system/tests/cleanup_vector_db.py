import os
import shutil
import sys

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import Config


def clean_vector_databases():
    """
    Clean up existing vector databases to start fresh.
    This will remove all existing vector database files.
    """
    vector_db_path = Config().VDBs_folder
    
    if os.path.exists(vector_db_path):
        print(f"Removing existing vector databases from: {vector_db_path}")
        try:
            shutil.rmtree(vector_db_path)
            print("✅ Successfully removed all existing vector databases")
            print("You can now run the RAG pipeline to create fresh databases")
        except Exception as e:
            print(f"❌ Error removing vector databases: {e}")
    else:
        print(f"No existing vector databases found at: {vector_db_path}")


if __name__ == "__main__":
    print("Vector Database Cleanup Utility")
    print("=" * 40)
    
    response = input("This will delete all existing vector databases. Are you sure? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        clean_vector_databases()
    else:
        print("Operation cancelled.")
