
import asyncio
import parlant.sdk as p
from security.security_interceptor import configure_hooks,configure_container
from mistral_service import load_mistral_service
from runpod_mistral_service import load_runpod_mistral_service
from guidlines import create_guidelines

async def main():
  async with p.Server(
    nlp_service=load_mistral_service,
    customer_store="mongodb://localhost:27017",
    session_store="mongodb://localhost:27017",
    configure_hooks=configure_hooks,
    configure_container=configure_container
  ) as server:
    agent = await server.create_agent(
    name="BH Assurance AI",
    description="""You are BH Assurance AI, a friendly and knowledgeable assistant for BH Assurance. 
You help clients understand coverage options, manage claims, and get information about BH Assurance services. 
Always explain clearly in simple language, show empathy when users are confused, and ensure they feel supported. 
If you don’t know the answer, be transparent and offer to connect them with a human representative."""
)


    await create_guidelines(agent)

asyncio.run(main())