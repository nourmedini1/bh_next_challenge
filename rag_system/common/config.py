class Config:
    """
    Configuration class to manage settings for the chatbot.
    """
    model_name: str = "BAAI/bge-m3"
    VDBs_folder: str = "vector_db"
    clean_data_path: str = "vector_stores_creation/documents/clean_data"
    distance_strategy: str = "cosine"