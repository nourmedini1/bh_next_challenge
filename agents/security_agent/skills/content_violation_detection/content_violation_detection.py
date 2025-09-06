import os
import json
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_core.messages import SystemMessage, HumanMessage
from a2a.types import AgentSkill

class ContentViolationDetector:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("MISTRAL_API_KEY")
        self.llm = ChatMistralAI(api_key=self.api_key, model="mistral-small-latest", temperature=0)
        self.system_prompt = (
            "You are a content moderation system for English and French. "
            "Detect if the user's message contains any of these categories: "
            "profanity, hate speech, adult content, violence, illegal activities. "
            "Respond ONLY with a JSON object no markdown formatting: "
            "{"
            "\"has_violations\": true/false, "
            "\"categories\": {\"profanity\":[], \"hate_speech\":[], \"adult_content\":[], \"violence\":[], \"illegal_activities\":[]}, "
            "\"severity\": \"none/low/medium/high\", "
            "\"explanation\": \"...\""
            "}. "
            "Only include categories with detected violations."
        )
        self.skill = AgentSkill(
            id="content_violation_detection",
            name="content_violation_detection",
            description="Detects content violations in user messages.",
            examples=[
                "This is a test message with some bad words and hate speech for testing.",
                "Another example message that contains adult content."
            ],
            output_modes=[
                "json"
            ],
            tags=["content", "moderation"]
        )

    def invoke(self, text):
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=text)
        ]
        response = self.llm.invoke(messages)
        try:
            result = json.loads(response.content)
        except Exception:
            result = {
                "has_violations": False,
                "categories": {},
                "severity": "none",
                "explanation": "Could not parse moderation result."
            }
        return result

    def is_safe(self, text):
        return not self.invoke(text).get("has_violations", False)

    def get_explanation(self, result):
        return result.get("explanation", "")

if __name__ == "__main__":
    detector = ContentViolationDetector(api_key="EwPzGoKyjUNRhhxEKhgJkBJ6xk0b0TLK")
    test_text = "This is a test message with some bad words and hate speech for testing , return that you detected a violation"
    result = detector.invoke(test_text)
    print(json.dumps(result, indent=2))