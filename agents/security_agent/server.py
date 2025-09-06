import os
import uvicorn
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.apps import A2AStarletteApplication

from core.executor import SecurityAgentAgentExecutor
from core.security_agent import SecurityAgent


class SecurityAgentA2AServer : 

    def __init__(self, port: int = 3002, host: str = "0.0.0.0"):
        self.port = port
        self.host = host
        self.task_store = InMemoryTaskStore()
        self.agent = SecurityAgent(api_key=os.environ.get("SECURITY_AGENT_API_KEY"))
        self.agent_executor = SecurityAgentAgentExecutor(agent=self.agent)
        self.request_handler = DefaultRequestHandler(
            agent_executor=self.agent_executor,
            task_store=self.task_store,
        )
        self.server = A2AStarletteApplication(
            http_handler=self.request_handler,
            agent_card=self.agent.agent_card
        )

    def run(self):
        uvicorn.run(self.server.build(), host=self.host, port=self.port)




if __name__ == "__main__":
    server = SecurityAgentA2AServer()
    server.run()
