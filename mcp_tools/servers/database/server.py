import os
import httpx
import uvicorn
from fastmcp import FastMCP
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

# Constants
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:2002/api/v1/agent")
DEFAULT_TIMEOUT = 30.0  # seconds

# Initialize MCP server
mcp = FastMCP(
    name="agent-access-service",
    version="1.0.0",
)

# ===== USER INFO TOOLS =====
@mcp.tool(
    title="Get Complete User Information",
    name="get_complete_user_info",
    description="Get complete user information including account and profile data for both individuals and companies",
    tags=["user", "profile"],
    output_schema={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "user_info": {
                "type": "object",
                "properties": {
                    "account": {"type": "object"},
                    "profile": {"type": "object"},
                    "profile_type": {"type": "string"}
                }
            },
            "error": {"type": "string"}
        },
        "required": ["success"]
    }
)
async def get_complete_user_info(ref_personne: int) -> dict:
    """Get complete user information including account and profile data"""
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        response = await client.get(
            f"{API_BASE_URL}/user/{ref_personne}/info"
        )
        
        if response.status_code != 200:
            error_detail = f"Failed to get user info: {response.status_code}"
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_detail = error_data["detail"]
            except:
                pass
            return {"success": False, "error": error_detail}
        
        return {"success": True, "user_info": response.json()}

# ===== CONTRACT TOOLS =====
@mcp.tool(
    title="Get User Contracts",
    name="get_user_contracts",
    description="Get user's insurance contracts with pagination",
    tags=["contracts"],
    output_schema={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "contracts": {
                "type": "object",
                "properties": {
                    "items": {"type": "array"},
                    "total": {"type": "integer"},
                    "page": {"type": "integer"},
                    "size": {"type": "integer"},
                    "pages": {"type": "integer"}
                }
            },
            "error": {"type": "string"}
        },
        "required": ["success"]
    }
)
async def get_user_contracts(ref_personne: int, page: int = 1, size: int = 20) -> dict:
    """Get user's insurance contracts with pagination"""
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        response = await client.get(
            f"{API_BASE_URL}/user/{ref_personne}/contracts",
            params={"page": page, "size": size}
        )
        
        if response.status_code != 200:
            error_detail = f"Failed to get contracts: {response.status_code}"
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_detail = error_data["detail"]
            except:
                pass
            return {"success": False, "error": error_detail}
        
        return {"success": True, "contracts": response.json()}

@mcp.tool(
    title="Get Contract Details",
    name="get_contract_details",
    description="Get specific contract details by contract number for a user",
    tags=["contracts"],
    output_schema={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "contract": {"type": "object"},
            "error": {"type": "string"}
        },
        "required": ["success"]
    }
)
async def get_contract_details(ref_personne: int, num_contrat: str) -> dict:
    """Get specific contract details by contract number for a user"""
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        response = await client.get(
            f"{API_BASE_URL}/user/{ref_personne}/contracts/{num_contrat}"
        )
        
        if response.status_code != 200:
            error_detail = f"Failed to get contract details: {response.status_code}"
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_detail = error_data["detail"]
            except:
                pass
            return {"success": False, "error": error_detail}
        
        return {"success": True, "contract": response.json()}

# ===== CLAIMS TOOLS =====
@mcp.tool(
    title="Get User Claims",
    name="get_user_claims",
    description="Get user's insurance claims with pagination",
    tags=["claims"],
    output_schema={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "claims": {
                "type": "object",
                "properties": {
                    "items": {"type": "array"},
                    "total": {"type": "integer"},
                    "page": {"type": "integer"},
                    "size": {"type": "integer"},
                    "pages": {"type": "integer"}
                }
            },
            "error": {"type": "string"}
        },
        "required": ["success"]
    }
)
async def get_user_claims(ref_personne: int, page: int = 1, size: int = 20) -> dict:
    """Get user's insurance claims with pagination"""
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        response = await client.get(
            f"{API_BASE_URL}/user/{ref_personne}/claims",
            params={"page": page, "size": size}
        )
        
        if response.status_code != 200:
            error_detail = f"Failed to get claims: {response.status_code}"
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_detail = error_data["detail"]
            except:
                pass
            return {"success": False, "error": error_detail}
        
        return {"success": True, "claims": response.json()}

@mcp.tool(
    title="Get Claim Details",
    name="get_claim_details",
    description="Get specific claim details by claim number for a user",
    tags=["claims"],
    output_schema={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "claim": {"type": "object"},
            "error": {"type": "string"}
        },
        "required": ["success"]
    }
)
async def get_claim_details(ref_personne: int, num_sinistre: str) -> dict:
    """Get specific claim details by claim number for a user"""
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        response = await client.get(
            f"{API_BASE_URL}/user/{ref_personne}/claims/{num_sinistre}"
        )
        
        if response.status_code != 200:
            error_detail = f"Failed to get claim details: {response.status_code}"
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_detail = error_data["detail"]
            except:
                pass
            return {"success": False, "error": error_detail}
        
        return {"success": True, "claim": response.json()}

# ===== HELPER TOOLS =====
@mcp.tool(
    title="Check User Existence",
    name="check_user_existence",
    description="Check if a user exists by reference number",
    tags=["user"],
    output_schema={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "exists": {"type": "boolean"},
            "error": {"type": "string"}
        },
        "required": ["success"]
    }
)
async def check_user_existence(ref_personne: int) -> dict:
    """Check if a user exists by reference number"""
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        response = await client.get(
            f"{API_BASE_URL}/user/{ref_personne}/info"
        )
        
        if response.status_code == 200:
            return {"success": True, "exists": True}
        elif response.status_code == 404:
            return {"success": True, "exists": False}
        else:
            error_detail = f"Failed to check user existence: {response.status_code}"
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_detail = error_data["detail"]
            except:
                pass
            return {"success": False, "error": error_detail}

if __name__ == "__main__":
    # Set host and port from environment variables or use defaults
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 4003))
    
    print(f"Starting Agent Access MCP Server on {host}:{port}")
    print(f"API Base URL: {API_BASE_URL}")
    
    uvicorn.run(mcp.sse_app(), host=host, port=port)