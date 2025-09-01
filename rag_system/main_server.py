"""
Main FastAPI application with separated concerns.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.models import RootResponse, HealthResponse
from api.config import get_all_store_names
from api.vector_store_service import VectorStoreService
from api import routes


# Global service instance
vector_store_service = VectorStoreService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    print("Starting RAG Vector Store Server...")
    
    # Set the global service instance in routes module
    routes.vector_store_service = vector_store_service
    
    # Load all vector stores
    await vector_store_service.load_all_vector_stores()
    
    print("Server startup completed!")
    yield
    
    # Shutdown
    print("Shutting down server...")


# Initialize FastAPI app
app = FastAPI(
    title="RAG Vector Store Server",
    description="""
    ## RAG Vector Store Server

    This FastAPI server provides endpoints for querying different insurance document vector stores.
    Each vector store is pre-loaded on startup for optimal performance.

    ### Vector Stores:
    - **1-CG-Vie**: Life insurance documents (11 products covering life insurance, retirement, savings, pension plans)
    - **2-CG-Santé**: Health insurance documents (group health insurance and medical coverage)
    - **3-CG-Transport**: Transport & marine insurance documents (7 products for cargo, shipping, vessel insurance)
    - **4-CG-IARD**: Property & casualty insurance documents (16+ products for home, business, liability, property risks)
    - **5-CG-Engineering**: Engineering & construction insurance documents (4 products for construction, assembly, contractor risks)
    - **6-CG-Automobile**: Automobile insurance documents (motor vehicle insurance coverage)
    - **7-Assurance-BH-Connaissances-Generales**: BH Assurance general knowledge (comprehensive documentation covering procedures, regulations, and services)

    ### Usage:
    1. Use the `/stores` endpoint to see all available vector stores and their status
    2. Query specific vector stores using `/query/{store-name}` endpoints
    3. Check server health with `/health` endpoint
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the routes
app.include_router(routes.router)


@app.get("/", response_model=RootResponse)
async def root():
    """Root endpoint with server information."""
    return RootResponse(
        message="RAG Vector Store Server",
        available_stores=get_all_store_names(),
        loaded_stores=vector_store_service.get_loaded_stores(),
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    stats = vector_store_service.get_store_stats()
    return HealthResponse(
        status="healthy",
        loaded_stores=stats["loaded_stores"],
        total_stores=stats["total_stores"]
    )
