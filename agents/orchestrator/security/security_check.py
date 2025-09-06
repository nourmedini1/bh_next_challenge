import asyncio
from typing import Any, Dict
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import Message, MessageSendParams, Role, SendMessageRequest, TextPart
import httpx
import uuid


async def is_malicious_or_violation(query: str, base_url: str = "http://localhost:3002") -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=30.0) as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        agent_card = await resolver.get_agent_card()
        a2a_client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)
        message = Message(
            role=Role.user,
            messageId=str(uuid.uuid4()),
            parts=[TextPart(text=query)],
        )
        request = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(message=message),
        )
        response = await a2a_client.send_message(request)
        return response.root.result.parts[0].model_dump().get("data").get("content")


if __name__ == "__main__":
    response = asyncio.run(is_malicious_or_violation("This is a normal message."))
    print(f"Malicious or Violation Detected: {response}")