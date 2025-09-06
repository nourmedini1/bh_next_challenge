
#run the rag pipeline to initialize the vector database
from vector_stores_creation.rag_pipeline import RAGPipeline
from common.config import Config
if __name__ == "__main__":
    rag_pipeline = RAGPipeline()
    rag_pipeline.initialize_vector_db(Config().clean_data_path)
    print("Vector database initialized successfully.")