from mcp import ClientSession
from mcp.client.sse import sse_client
import json
import asyncio
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import parlant.sdk as p
from observability.log_producer import LogProducer,log_tool_call


log_producer = LogProducer(client_id="mcp-quotes-tool-producer")
TOOL_TOPICS = {
    'get_automobile_insurance_quote': 'tool_get_automobile_insurance_quote'
}


class QuoteRequest(BaseModel):
    """Parameters needed to get an automobile insurance quote"""
    n_cin: str = Field(description="National ID number of the vehicle owner")
    valeur_venale: int = Field(description="Current market value of the vehicle in currency units")
    nature_contrat: str = Field(description="Contract type: 'n' for new, 'r' for renewal")
    nombre_place: int = Field(description="Number of seats in the vehicle")
    valeur_a_neuf: int = Field(description="Value of the vehicle when new in currency units")
    date_premiere_mise_en_circulation: str = Field(description="Date of first registration in YYYY-MM-DD format")
    capital_bris_de_glace: int = Field(description="Glass breakage coverage amount")
    capital_dommage_collision: int = Field(description="Collision damage coverage amount")
    puissance: int = Field(description="Vehicle engine power")
    classe: int = Field(description="Vehicle class category")


@p.tool()
@log_tool_call(log_producer, TOOL_TOPICS['get_automobile_insurance_quote'])
async def get_automobile_insurance_quote(
    context : p.ToolContext,
    n_cin: str,
    valeur_venale: int,
    nature_contrat: str,
    nombre_place: int,
    valeur_a_neuf: int,
    date_premiere_mise_en_circulation: str,
    capital_bris_de_glace: int,
    capital_dommage_collision: int,
    puissance: int,
    classe: int
) -> p.ToolResult : 
    """
    Generates automobile insurance quotes based on vehicle specifications and owner information.
    
    This tool connects to the MCP quote generation service to calculate insurance premiums
    for automobile coverage. It provides detailed quotes with different coverage options,
    guarantees, and pricing.
    
    Args:
        n_cin: Owner's ID number
        valeur_venale: Current market value of the vehicle
        nature_contrat: Contract type ('r' for civil responsibility and liability , 'n' for all risks (comprehensive))
        nombre_place: Number of seats in the vehicle
        valeur_a_neuf: Value of the vehicle when new
        date_premiere_mise_en_circulation: Date of first registration (YYYY-MM-DD)
        capital_bris_de_glace: Glass breakage coverage amount
        capital_dommage_collision: Collision damage coverage amount
        puissance: Vehicle engine power
        classe: Vehicle class
               
    Returns:
        A JSON object containing quote information including:
        - Available insurance packages
        - Premium amounts (monthly and annual)
        - Coverage details and limits
        - Applicable guarantees and exclusions
    """
    # Create a properly formatted request dictionary
    vehicle_details = {
        "n_cin": n_cin,
        "valeur_venale": valeur_venale,
        "nature_contrat": nature_contrat,
        "nombre_place": nombre_place,
        "valeur_a_neuf": valeur_a_neuf,
        "date_premiere_mise_en_circulation": date_premiere_mise_en_circulation,
        "capital_bris_de_glace": capital_bris_de_glace,
        "capital_dommage_collision": capital_dommage_collision,
        "puissance": puissance,
        "classe": classe
    }
    
    # Connect to the MCP service and get the quote
    async with sse_client(url="http://localhost:4002/sse") as (read, write):
        async with ClientSession(read_stream=read, write_stream=write) as session:
            await session.initialize()
            await session.send_ping()
            response = await session.call_tool(
                name="quote_generation", 
                arguments={"quote_request": vehicle_details}
            )
            response = json.loads(response.content[0].text)
            
            if response.get("success", False):
                return p.ToolResult(data = response["quotes"])
            else:
                return p.ToolResult(data =  response.get("errors", ["Unknown error occurred"]))


# For testing
if __name__ == "__main__":
    async def main():
        # Test with sample data
        params = {
            "n_cin": "08478931",
            "valeur_venale": 60000,
            "nature_contrat": "n",
            "nombre_place": 5,
            "valeur_a_neuf": 60000,
            "date_premiere_mise_en_circulation": "2022-02-28",
            "capital_bris_de_glace": 900,
            "capital_dommage_collision": 60000,
            "puissance": 6,
            "classe": 3
        }
        
        quote = await get_automobile_insurance_quote(**params)
        print(json.dumps(quote, indent=2))
    
    asyncio.run(main())