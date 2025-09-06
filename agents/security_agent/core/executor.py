import traceback
from a2a.types import DataPart
from a2a.server.agent_execution import AgentExecutor
from a2a.server.request_handlers.default_request_handler import RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_parts_message

from core.security_agent import SecurityAgent


class SecurityAgentAgentExecutor(AgentExecutor):

    def __init__(self, agent: SecurityAgent):
        self.agent = agent

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        message_json = context.message.model_dump()
        print(f"Received message: {message_json}")
        if not message_json["parts"]:
            await event_queue.enqueue_event(new_agent_parts_message(parts=[DataPart(
                data={"type": "application/json", "content": {"error": "No message parts found"}}
            )]))
            return

        try:
            part = message_json["parts"][0]
            user_query = part.get("text")
        except Exception as e:
            await event_queue.enqueue_event(new_agent_parts_message(parts=[DataPart(
                data={"type": "application/json", "content": {"error": f"Error extracting json payload: {str(e)}"}}
            )]))
            return
        try: 
            agent_response = self.agent.invoke(user_query)
            await event_queue.enqueue_event(new_agent_parts_message(parts=[DataPart(
            data={"type": "application/json", "content": agent_response}
            )]))

        except Exception as e:
            traceback.print_exc()
            await event_queue.enqueue_event(new_agent_parts_message(parts=[DataPart(
                data={"type": "application/json", "content": {"error": f"Error processing query: {str(e)}"}}
            )]))
            return

    async def cancel(self, context, event_queue):
        return await super().cancel(context, event_queue)