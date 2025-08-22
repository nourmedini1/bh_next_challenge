from datetime import datetime
import json
import traceback
from a2a.types import DataPart
from a2a.server.agent_execution import AgentExecutor
from a2a.server.request_handlers.default_request_handler import RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.apps import A2AStarletteApplication
from a2a.utils import new_agent_parts_message

from core.attachment_handling_agent import AttachmentHandler


class AttachmentHandlerAgentExecutor(AgentExecutor):

    def __init__(self, agent: AttachmentHandler):
        self.agent = agent

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        print(json.dumps(context.message.model_dump(), indent=2))
        message_json = context.message.model_dump()
        if not message_json["parts"]:
            await event_queue.enqueue_event(new_agent_parts_message(parts=[DataPart(
                data={"type": "application/json", "content": {"error": "No message parts found"}}
            )]))
            return

        try:
            # Get the first part from the message
            part = message_json["parts"][0]
            print(part)
            file_data = part.get("data").get("content").get("file_data")
        except Exception as e:
            await event_queue.enqueue_event(new_agent_parts_message(parts=[DataPart(
                data={"type": "application/json", "content": {"error": f"Error extracting json payload: {str(e)}"}}
            )]))
            return

        print(f"file data is {file_data}")
        print(f"file name is {file_data.get('name')}")
        print(f"file declared type is {file_data.get('declared_type')}")
        print(f"file size is {file_data.get('size')}")
        print(f"file content is {file_data.get('content')}")


        file_data = {
            "name": file_data.get("name", "unknown"),
            "size": file_data.get("size", 0),
            "declared_type": file_data.get("declared_type", "application/octet-stream"),
            "content": file_data.get("content", b"")
        }
        try: 
            agent_response = self.agent.invoke(file_data)
            await event_queue.enqueue_event(new_agent_parts_message(parts=[DataPart(
            data={"type": "application/json", "content": agent_response}
            )]))

        except Exception as e:
            traceback.print_exc()
            await event_queue.enqueue_event(new_agent_parts_message(parts=[DataPart(
                data={"type": "application/json", "content": {"error": f"Error processing attachment: {str(e)}"}}
            )]))
            return

    async def cancel(self, context, event_queue):
        return await super().cancel(context, event_queue)