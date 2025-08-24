from core.data_extraction import DataExtractor
from fastmcp import FastMCP
import uvicorn


mcp = FastMCP(
    name="Insurance-products-data-extractor",
    version="0.1.0",
)


extractor = DataExtractor(
    model_name="mistral-small-latest",
    api_key="wIUxlrv4SvHiP3VY1PuIHNhBB4IGRcep"
)

@mcp.tool(
        title="Extract Insurance Products",
        name="extract_insurance_products", 
        description="Process a user query and return the most relevant insurance products",
        tags=["data-extraction"],
        output_schema={
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
                "products": {
                    "type": "object",
                    "additionalProperties": {  
                        "type": "object",
                        "properties": {
                            "category": {"type": "string"},
                            "subcategory": {"type": "string"},
                            "guarantees": {
                                "type": "object",
                                "additionalProperties": {  
                                    "type": "object",
                                    "properties": {
                                        "description": {"type": "string"},
                                        "targeted_profiles": {"type": "string"}
                                    },
                                    "required": ["description", "targeted_profiles"]
                                }
                            }
                        },
                        "required": ["category", "subcategory", "guarantees"]
                    }
                }
            },
            "required": ["success", "message", "products"]
        }
        )
async def extract_insurance_products(query: str) -> dict:
    response = await extractor.process_query(query)
    return response

if __name__ == "__main__":
    uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=4001)