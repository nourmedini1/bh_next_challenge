import parlant.sdk as p
from mcp import ClientSession
from mcp.client.sse import sse_client
import json
from observability.log_producer import LogProducer,log_tool_call
# Constants
MCP_SERVICE_URL = "http://localhost:4003/sse"

log_producer = LogProducer(client_id="database-access-tool-producer")
TOOL_TOPICS = {
    'get_complete_user_info': 'tool_get_complete_user_info',
    'get_user_contracts': 'tool_get_user_contracts',
    'get_contract_details': 'tool_get_contract_details',
    'get_user_claims': 'tool_get_user_claims',
    'get_claim_details': 'tool_get_claim_details',
    'check_user_existence': 'tool_check_user_existence'
}

@p.tool()
@log_tool_call(log_producer, TOOL_TOPICS['get_complete_user_info'])
async def get_complete_user_info(context: p.ToolContext) -> p.ToolResult:
    """
    Get complete user information including account and profile data for the current customer.
    
    This tool retrieves detailed user information including name, email, address, profession, 
    date of birth, and other relevant profile details from the database.
    """
    ref_personne = int("715")

    async with sse_client(url=MCP_SERVICE_URL) as (read, write):
        async with ClientSession(read_stream=read, write_stream=write) as session:
            await session.initialize()
            await session.send_ping()
            response = await session.call_tool(
                name="get_complete_user_info", 
                arguments={"ref_personne": ref_personne}
            )
            response = json.loads(response.content[0].text) if response.content else {}
            
            return p.ToolResult(data=response)

@p.tool()
@log_tool_call(log_producer, TOOL_TOPICS['get_user_contracts'])
async def get_user_contracts(context: p.ToolContext, page: int = 1, size: int = 20) -> p.ToolResult:
    """
    Get the user's insurance contracts with pagination.
    
    This tool retrieves a list of insurance contracts associated with the current user,
    including details such as contract numbers, types, start and end dates, and status.
    
    Args:
        page: Page number for pagination (defaults to 1)
        size: Number of items per page (defaults to 20)
    """
    ref_personne = int("715")

    async with sse_client(url=MCP_SERVICE_URL) as (read, write):
        async with ClientSession(read_stream=read, write_stream=write) as session:
            await session.initialize()
            await session.send_ping()
            response = await session.call_tool(
                name="get_user_contracts", 
                arguments={"ref_personne": ref_personne, "page": page, "size": size}
            )
            response = json.loads(response.content[0].text) if response.content else {}
            
            return p.ToolResult(data=response)

@p.tool()
@log_tool_call(log_producer, TOOL_TOPICS['get_contract_details'])
async def get_contract_details(context: p.ToolContext, num_contrat: str) -> p.ToolResult:
    """
    Get detailed information about a specific insurance contract.
    
    This tool retrieves comprehensive details about a specific contract including coverage limits,
    premium amounts, payment schedule, and policy-specific information.
    
    Args:
        num_contrat: Contract number to retrieve details for
    """
    ref_personne = int("715")
    async with sse_client(url=MCP_SERVICE_URL) as (read, write):
        async with ClientSession(read_stream=read, write_stream=write) as session:
            await session.initialize()
            await session.send_ping()
            response = await session.call_tool(
                name="get_contract_details", 
                arguments={"ref_personne": ref_personne, "num_contrat": num_contrat}
            )
            response = json.loads(response.content[0].text) if response.content else {}
            
            return p.ToolResult(data=response)

@p.tool()
@log_tool_call(log_producer, TOOL_TOPICS['get_user_claims'])
async def get_user_claims(context: p.ToolContext, page: int = 1, size: int = 20) -> p.ToolResult:
    """
    Get the user's insurance claims with pagination.
    
    This tool retrieves a list of insurance claims filed by the current user,
    including claim numbers, dates, types, status, and associated contracts.
    
    Args:
        page: Page number for pagination (defaults to 1)
        size: Number of items per page (defaults to 20)
    """
    ref_personne = int("715")

    async with sse_client(url=MCP_SERVICE_URL) as (read, write):
        async with ClientSession(read_stream=read, write_stream=write) as session:
            await session.initialize()
            await session.send_ping()
            response = await session.call_tool(
                name="get_user_claims", 
                arguments={"ref_personne": ref_personne, "page": page, "size": size}
            )
            response = json.loads(response.content[0].text) if response.content else {}
            
            return p.ToolResult(data=response)

@p.tool()
@log_tool_call(log_producer, TOOL_TOPICS['get_claim_details'])
async def get_claim_details(context: p.ToolContext, num_sinistre: str) -> p.ToolResult:
    """
    Get detailed information about a specific insurance claim.
    
    This tool retrieves comprehensive details about a specific claim including date reported,
    incident details, claim status, settlement information, and related documentation.
    
    Args:
        num_sinistre: Claim number to retrieve details for
    """
    ref_personne = int("715")

    async with sse_client(url=MCP_SERVICE_URL) as (read, write):
        async with ClientSession(read_stream=read, write_stream=write) as session:
            await session.initialize()
            await session.send_ping()
            response = await session.call_tool(
                name="get_claim_details", 
                arguments={"ref_personne": ref_personne, "num_sinistre": num_sinistre}
            )
            response = json.loads(response.content[0].text) if response.content else {}
            
            return p.ToolResult(data=response)

@p.tool()
@log_tool_call(log_producer, TOOL_TOPICS['check_user_existence'])
async def check_user_existence(context: p.ToolContext) -> p.ToolResult:
    """
    Verify if the current user exists in the database system.
    
    This tool checks whether the current customer ID corresponds to a valid user
    in the insurance database system.
    """
    ref_personne = int("715")

    async with sse_client(url=MCP_SERVICE_URL) as (read, write):
        async with ClientSession(read_stream=read, write_stream=write) as session:
            await session.initialize()
            await session.send_ping()
            response = await session.call_tool(
                name="check_user_existence", 
                arguments={"ref_personne": ref_personne}
            )
            response = json.loads(response.content[0].text) if response.content else {}
            
            return p.ToolResult(data=response)
        

if __name__ == "__main__":
    import asyncio

    context = p.ToolContext(
        customer_id="715",
        agent_id="123",
        session_id="abc-session"
        )
    
    response = asyncio.run(get_user_contracts(context))
    print(response)