"""
Pydantic models for API request and response schemas.
"""

from pydantic import BaseModel
from typing import List, Dict, Optional


class QueryRequest(BaseModel):
    """Request model for vector store queries."""
    query: str
    k: Optional[int] = 5  # Number of results to return


class DocumentResult(BaseModel):
    """Model for individual document search results."""
    content: str
    metadata: Dict
    score: Optional[float] = None


class QueryResponse(BaseModel):
    """Response model for vector store query results."""
    query: str
    results: List[DocumentResult]
    total_results: int
    vector_store: str


class StoreInfo(BaseModel):
    """Model for vector store information."""
    name: str
    description: str
    products: List[str]
    loaded: bool
    endpoint: str


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    loaded_stores: int
    total_stores: int


class RootResponse(BaseModel):
    """Response model for root endpoint."""
    message: str
    available_stores: List[str]
    loaded_stores: List[str]
    version: str


class AddDocumentResponse(BaseModel):
    """Response model for adding documents to vector store."""
    message: str
    store_name: str
    file_name: str
    chunks_added: int
