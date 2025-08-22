from datetime import datetime
import uvicorn
from a2a.types import DataPart
from a2a.server.agent_execution import AgentExecutor
from a2a.server.request_handlers.default_request_handler import RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.apps import A2AStarletteApplication
from a2a.utils import new_agent_parts_message

from core.executor import AttachmentHandlerAgentExecutor
from core.attachment_handling_agent import AttachmentHandler
from core.config import AgentConfig

task_store = InMemoryTaskStore()

config = {
    # Embedded Code Detector Config Params
    "max_compression_ratio": 1000.0,
    "max_nested_archives": 5,

    # Gateway Validator Config Params
    "max_allowed_file_size": 10485760,  # 10 MB
    "allowed_file_types": [
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/pdf",
        "text/plain",
        "text/csv",
        "text/markdown",
        "text/x-markdown",
        "application/rtf",
        "application/vnd.oasis.opendocument.text",
        "application/vnd.oasis.opendocument.spreadsheet",
        "application/vnd.oasis.opendocument.presentation"
    ],

    # Malware Scanner Config Params
    "host": "localhost",
    "port": 3310,
    "chunk_size": 4096,

    # Prompt Injection Detection Config Params
    "prompt_injection_model": "mistral-small-latest",
    "prompt_injection_api_key": "wIUxlrv4SvHiP3VY1PuIHNhBB4IGRcep",
    "prompt_injection_RBD_threshold": 0.35,
    "prompt_injection_LLM_threshold": 0.8,
    "prompt_injection_doubt_threshold": 0.2
}


agent = AttachmentHandler(config=config)
agent_executor = AttachmentHandlerAgentExecutor(agent=agent)

request_handler = DefaultRequestHandler(
    agent_executor=agent_executor,
    task_store=task_store,
)

server = A2AStarletteApplication(
    http_handler=request_handler,
    agent_card= agent.agent_card
)

host = "0.0.0.0"
port = 3001

if __name__ == "__main__":
    uvicorn.run(server.build(), host=host, port=port)