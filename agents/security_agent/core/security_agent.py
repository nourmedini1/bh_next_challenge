
from typing import Any, Dict, Literal, TypedDict
from skills.content_violation_detection.content_violation_detection import ContentViolationDetector
from skills.prompt_injection_detection.prompt_injection_detector import PromptInjectionDetector
from a2a.types import AgentCard,AgentCapabilities
from langgraph.graph import StateGraph,END,START


class SecurityAgentState(TypedDict):
    query: str
    status: Literal["ACCEPTED","REJECTED","PENDING"]
    details: list[Dict[str, Any]]

    
class SecurityAgent:

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.pi_detector = PromptInjectionDetector(llm_api_key=api_key)
        self.content_violation_detector = ContentViolationDetector(api_key=api_key)
        self.skills = [
            self.pi_detector.skill,
            self.content_violation_detector.skill
        ]

        self.agent_card = AgentCard(
            id="security_agent",
            name="SecurityAgent",
            version="1.0.0",
            description="Detect and prevent security threats in user queries",
            examples=[
                "Detecting prompt injection attacks",
                "Identifying content violations in user queries"
            ],
            capabilities= AgentCapabilities(),
            default_input_modes= ["application/json"],
            default_output_modes= ["application/json"],
            skills=self.skills,
            url="http://0.0.0.0:3002/"
        )

        self.workflow = self.build_graph()

    def check_prompt_injection(self, state  : SecurityAgentState) -> SecurityAgentState:
        result = self.pi_detector.invoke(state["query"])
        if result.get("is_injection", True):
            state["status"] = "REJECTED"
        state["details"].append({
                "tool": "prompt_injection_detection",
                "result": result
            })
        return state
    

    def check_content_violation(self, state: SecurityAgentState) -> SecurityAgentState:
       result =  self.content_violation_detector.invoke(state["query"])
       if result.get("has_violations", True):
           state["status"] = "REJECTED"
       else:
           state["status"] = "ACCEPTED"
       state["details"].append({
           "tool": "content_violation_detection",
           "result": result
       })
       return state

    def conditional_node_after_prompt_injection_detection(self, state: SecurityAgentState) -> Literal["content_violation_detection","__end__"]:
        if state["status"] == "REJECTED":
            return "__end__"
        return "content_violation_detection"


    def build_graph(self) -> StateGraph:
        graph = StateGraph(SecurityAgentState)
        graph.add_node("prompt_injection_detection", self.check_prompt_injection)
        graph.add_node("content_violation_detection", self.check_content_violation)

        graph.add_edge(START, "prompt_injection_detection")
        graph.add_conditional_edges("prompt_injection_detection", self.conditional_node_after_prompt_injection_detection)
        graph.add_edge("content_violation_detection", END)
        return graph.compile()

    def invoke(self, query: str) -> Dict[str, Any]:
        initial_state: SecurityAgentState = {
            "query": query,
            "status": "PENDING",
            "details": []
        }
        return self.workflow.invoke(initial_state)

