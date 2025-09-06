import parlant.sdk as p
import httpx
from observability.log_producer import LogProducer,log_tool_call
import os


log_producer = LogProducer(client_id="rag-tool-producer")
TOOL_TOPICS = {
    'search_life_insurance_documents': 'tool_search_life_insurance_documents',
    'search_health_insurance_documents': 'tool_search_health_insurance_documents',
    'search_transport_marine_documents': 'tool_search_transport_marine_documents',
    'search_property_casualty_documents': 'tool_search_property_casualty_documents',
    'search_engineering_construction_documents': 'tool_search_engineering_construction_documents',
    'search_automobile_insurance_documents': 'tool_search_automobile_insurance_documents',
    'search_general_knowledge_documents': 'tool_search_general_knowledge_documents'
}



BASE_URL = os.environ.get("RAG_API_URL", "http://192.168.1.19:2004")
# Constants
RAG_API_URL = f"{BASE_URL}/query"

@p.tool()
@log_tool_call(log_producer, TOOL_TOPICS['search_life_insurance_documents'])
async def search_life_insurance_documents(context: p.ToolContext, query: str, k: int = 3) -> p.ToolResult:
    """
    Search Life Insurance Documents (Assurance Vie) for information.
    
    This tool queries the knowledge base for life insurance products including AMALI, ASSUR SENIOR, 
    DHAMEN series, HANA, HORIZON series, RAHMA, and retirement benefits.
    
    Use for questions about: life insurance, retirement planning, savings products, death benefits, 
    life coverage, pension plans, senior insurance.
    
    Args:
        query: The search query text
        k: Number of results to return (default: 3)
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{RAG_API_URL}/1-CG-Vie",
            json={"query": query, "k": k}
        )
        
        if response.status_code != 200:
            return p.ToolResult(data={
                "success": False,
                "error": f"Failed to query Life Insurance documents: {response.text}"
            })
        
        return p.ToolResult(data={
            "success": True,
            "results": response.json()
        })

@p.tool()
@log_tool_call(log_producer, TOOL_TOPICS['search_health_insurance_documents'])
async def search_health_insurance_documents(context: p.ToolContext, query: str, k: int = 3) -> p.ToolResult:
    """
    Search Health Insurance Documents (Assurance Santé) for information.
    
    This tool queries the knowledge base for health insurance documentation covering group health plans.
    
    Use for questions about: health insurance, medical coverage, group health plans, 
    healthcare benefits, illness coverage.
    
    Args:
        query: The search query text
        k: Number of results to return (default: 3)
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{RAG_API_URL}/2-CG-Santé",
            json={"query": query, "k": k}
        )
        
        if response.status_code != 200:
            return p.ToolResult(data={
                "success": False,
                "error": f"Failed to query Health Insurance documents: {response.text}"
            })
        
        return p.ToolResult(data={
            "success": True,
            "results": response.json()
        })

@p.tool()
@log_tool_call(log_producer, TOOL_TOPICS['search_transport_marine_documents'])
async def search_transport_marine_documents(context: p.ToolContext, query: str, k: int = 3) -> p.ToolResult:
    """
    Search Transport & Marine Insurance Documents for information.
    
    This tool queries the knowledge base for transport and marine insurance products covering 
    cargo and vessel insurance.
    
    Use for questions about: transport insurance, marine insurance, cargo coverage, 
    shipping insurance, boat insurance, vessel protection.
    
    Args:
        query: The search query text
        k: Number of results to return (default: 3)
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{RAG_API_URL}/3-CG-Transport",
            json={"query": query, "k": k}
        )
        
        if response.status_code != 200:
            return p.ToolResult(data={
                "success": False,
                "error": f"Failed to query Transport & Marine Insurance documents: {response.text}"
            })
        
        return p.ToolResult(data={
            "success": True,
            "results": response.json()
        })

@p.tool()
@log_tool_call(log_producer, TOOL_TOPICS['search_property_casualty_documents'])
async def search_property_casualty_documents(context: p.ToolContext, query: str, k: int = 3) -> p.ToolResult:
    """
    Search Property & Casualty Insurance Documents (IARD) for information.
    
    This tool queries the knowledge base for property and casualty insurance products 
    covering comprehensive property and business risks.
    
    Use for questions about: home insurance, property damage, theft, fire, liability, 
    professional insurance, card insurance, glass breakage, water damage, business interruption.
    
    Args:
        query: The search query text
        k: Number of results to return (default: 3)
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{RAG_API_URL}/4-CG-IARD",
            json={"query": query, "k": k}
        )
        
        if response.status_code != 200:
            return p.ToolResult(data={
                "success": False,
                "error": f"Failed to query Property & Casualty Insurance documents: {response.text}"
            })
        
        return p.ToolResult(data={
            "success": True,
            "results": response.json()
        })

@p.tool()
@log_tool_call(log_producer, TOOL_TOPICS['search_engineering_construction_documents'])
async def search_engineering_construction_documents(context: p.ToolContext, query: str, k: int = 3) -> p.ToolResult:
    """
    Search Engineering & Construction Insurance Documents for information.
    
    This tool queries the knowledge base for engineering and construction insurance products 
    covering construction and assembly risks.
    
    Use for questions about: construction insurance, engineering risks, building projects, 
    contractor insurance, construction equipment, assembly risks.
    
    Args:
        query: The search query text
        k: Number of results to return (default: 3)
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{RAG_API_URL}/3-CG-Engineering",
            json={"query": query, "k": k}
        )
        
        if response.status_code != 200:
            return p.ToolResult(data={
                "success": False,
                "error": f"Failed to query Engineering & Construction Insurance documents: {response.text}"
            })
        
        return p.ToolResult(data={
            "success": True,
            "results": response.json()
        })

@p.tool()
@log_tool_call(log_producer, TOOL_TOPICS['search_automobile_insurance_documents'])
async def search_automobile_insurance_documents(context: p.ToolContext, query: str, k: int = 3) -> p.ToolResult:
    """
    Search Automobile Insurance Documents for information.
    
    This tool queries the knowledge base for motor vehicle insurance documentation.
    
    Use for questions about: car insurance, vehicle coverage, auto insurance, motor vehicle protection.
    
    Args:
        query: The search query text
        k: Number of results to return (default: 3)
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{RAG_API_URL}/6-CG-Automobile",
            json={"query": query, "k": k}
        )
        
        if response.status_code != 200:
            return p.ToolResult(data={
                "success": False,
                "error": f"Failed to query Automobile Insurance documents: {response.text}"
            })
        
        return p.ToolResult(data={
            "success": True,
            "results": response.json()
        })

@p.tool()
@log_tool_call(log_producer, TOOL_TOPICS['search_general_knowledge_documents'])
async def search_general_knowledge_documents(context: p.ToolContext, query: str, k: int = 3) -> p.ToolResult:
    """
    Search BH Assurance General Knowledge Documents for information.
    
    This tool queries the knowledge base for comprehensive general knowledge about BH Assurance 
    policies, procedures, and services.
    
    Use for questions about: insurance definitions, policy procedures, Wininti application, 
    KYC processes, premium payments, claims declaration, digital services, regulatory compliance, 
    customer support, contract management, attestations, exclusions, fraud prevention.
    
    Args:
        query: The search query text
        k: Number of results to return (default: 3)
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{RAG_API_URL}/7-Assurance-BH-Connaissances-Generales",
            json={"query": query, "k": k}
        )
        
        if response.status_code != 200:
            return p.ToolResult(data={
                "success": False,
                "error": f"Failed to query BH Assurance General Knowledge documents: {response.text}"
            })
        
        return p.ToolResult(data={
            "success": True,
            "results": response.json()
        })


if __name__ == "__main__":
    import asyncio
    
    async def test():
        context = p.ToolContext()
        query = "What are the benefits of life insurance?"
        result = await search_life_insurance_documents(context, query)
        print(result.data)
    
    asyncio.run(test())