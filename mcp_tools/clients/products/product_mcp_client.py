import asyncio
import json
import httpx
from mcp import ClientSession
from mcp.client.sse import sse_client


async def main():
    async with sse_client(url="http://localhost:4001/sse") as (read,write) :
        async with ClientSession(read_stream=read, write_stream=write) as session:
            await session.initialize()
            await session.send_ping()


            response = await session.call_tool(name="extract_insurance_products", arguments={"query": "What are the insurance products available for health?"})
            response = json.loads(response.content[0].text)
            print(response["products"])

if __name__ == "__main__":
    asyncio.run(main())
