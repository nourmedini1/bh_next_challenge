from mcp import ClientSession
from mcp.client.sse import sse_client
import json
from observability.log_producer import LogProducer,log_tool_call

import parlant.sdk as p

log_producer = LogProducer(client_id="mcp-products-tool-producer")
TOOL_TOPICS = {
    'get_non_automobile_insurance_products_descriptions': 'tool_get_non_automobile_insurance_products_descriptions'
}

@p.tool()
@log_tool_call(log_producer, TOOL_TOPICS['get_non_automobile_insurance_products_descriptions'])
async def get_non_automobile_insurance_products_descriptions(context : p.ToolContext, query: str) -> p.ToolResult:
    """
    Retrieves information about non-automobile insurance products based on a user query.
    """
    async with sse_client(url="http://localhost:4001/sse") as (read, write):
        async with ClientSession(read_stream=read, write_stream=write) as session:
            await session.initialize()
            await session.send_ping()
            response = await session.call_tool(name="extract_insurance_products", arguments={"query": query})
            response = json.loads(response.content[0].text)
            return p.ToolResult(
                data=response["products"],
                )
        
if __name__ == "__main__":
    import asyncio
    async def main():
        params = {
            "query": "What health insurance options do you offer?"
        }
        context = p.ToolContext(
            agent_id="example_agent_id",
            session_id="example_conversation_id",
            customer_id="example_message_id"
        )
        quote = await get_non_automobile_insurance_products_descriptions(context, **params)
        print(quote)
    asyncio.run(main())