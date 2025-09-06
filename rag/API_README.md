# RAG Vector Store Server

A FastAPI-based server providing REST endpoints for querying insurance document vector stores.

## Project Structure

```
chatbot/
├── api/                          # API package
│   ├── __init__.py
│   ├── models.py                 # Pydantic models for requests/responses
│   ├── config.py                 # Vector store configurations
│   ├── vector_store_service.py   # Service layer for vector store operations
│   └── routes.py                 # FastAPI route definitions
├── main_server.py                # Main FastAPI application
├── run_server.py                 # Server startup script
├── test_server.py                # Test script for API endpoints
└── server.py                     # Legacy monolithic server (deprecated)
```

## Components

### 1. **models.py** - Data Models
- `QueryRequest`: Request schema for vector store queries
- `QueryResponse`: Response schema with search results
- `DocumentResult`: Individual document search result
- `StoreInfo`: Vector store metadata
- Health check and root endpoint models

### 2. **config.py** - Vector Store Configuration
- `VECTOR_STORE_CONFIG`: Complete configuration for all 7 vector stores
- Helper functions for accessing store metadata
- Contains descriptions, products, and use cases for each store

### 3. **vector_store_service.py** - Business Logic
- `VectorStoreService`: Core service class managing vector stores
- Handles loading/querying vector stores
- Provides statistics and health information
- Abstracts vector store operations from API layer

### 4. **routes.py** - API Endpoints
- FastAPI router with all query endpoints
- Dependency injection for service layer
- Individual endpoints for each vector store
- Comprehensive API documentation

### 5. **main_server.py** - Application Setup
- FastAPI application configuration
- Lifespan management for startup/shutdown
- Root and health endpoints
- Router integration

## Vector Stores

1. **1-CG-Vie** - Life Insurance (11 products)
2. **2-CG-Santé** - Health Insurance (1 product)
3. **3-CG-Transport** - Transport & Marine Insurance (7 products)
4. **4-CG-IARD** - Property & Casualty Insurance (16+ products)
5. **5-CG-Engineering** - Engineering & Construction Insurance (4 products)
6. **6-CG-Automobile** - Automobile Insurance (1 product)
7. **7-Assurance-BH-Connaissances-Generales** - BH Assurance General Knowledge (comprehensive documentation)

## Usage

### Start the Server
```bash
python run_server.py
```

### Test the Server
```bash
python test_server.py
```

### API Endpoints

- `GET /` - Server information
- `GET /health` - Health check
- `GET /query/stores` - List all vector stores
- `POST /query/{store-name}` - Query specific vector store

### Example Query
```bash
curl -X POST "http://localhost:8000/query/1-CG-Vie" \
     -H "Content-Type: application/json" \
     -d '{"query": "life insurance benefits", "k": 5}'
```

## Benefits of This Structure

1. **Separation of Concerns**: Each file has a single responsibility
2. **Maintainability**: Easy to modify individual components
3. **Testability**: Service layer can be tested independently
4. **Scalability**: Easy to add new vector stores or endpoints
5. **Type Safety**: Comprehensive Pydantic models
6. **Documentation**: Auto-generated API docs via FastAPI
