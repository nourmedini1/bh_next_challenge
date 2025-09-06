from core.quote_api import QuoteAPI
from core.models.quote_request import QuoteRequest
from utils import validate_quote_request
from fastmcp import FastMCP
import uvicorn
from typing import Dict, Any



mcp = FastMCP(
    name="quote-generator",
    version="0.1.0",
)


api = QuoteAPI()


@mcp.tool(
    title="Quote Generation",
    name="quote_generation", 
    description="Generates a quote based on the user's input",
    tags=["quote", "automobiles", "insurance", "prices"],
    output_schema={
        "type": "object",  
        "properties": {
            "success": {"type": "boolean"},
            "errors": {
                "type": "array",
                "items": {"type": "string"}
            },
            "quotes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "codeProduit": {"type": "string"},
                        "garantieCourtierModels": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "capital": {"type": "string"},
                                    "codeFranchise": {"type": "string"},
                                    "codeGarantie": {"type": "string"},
                                    "libGarantie": {"type": "string"}
                                }
                            }
                        },
                        "montantPrimeDivisePar12": {"type": "number"},
                        "montantTotalPrime": {"type": "number"},
                        "packApplicable": {"type": "boolean"},
                        "packDisponible": {"type": "string"}
                    },
                    "required": ["codeProduit", "montantTotalPrime", "packApplicable"]
                }
            }
        },
        "required": ["success", "quotes"]
    }
)
async def generate_quote(quote_request: Dict[str, Any]) -> dict:
    validation_result = validate_quote_request(quote_request)

    if not validation_result["success"]:
        return {
            "success": False,
            "errors": validation_result["errors"],
            "quotes": []
        }
    
    try:
        quote_request = QuoteRequest(**quote_request)
        
        quotes = api.get_quote(quote_request)
        
        return {
            "success": True,
            "quotes": quotes
        }
    except Exception as e:
        return {
            "success": False,
            "errors": [f"Error generating quote: {str(e)}"],
            "quotes": []
        }

if __name__ == "__main__":
    uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=4002)