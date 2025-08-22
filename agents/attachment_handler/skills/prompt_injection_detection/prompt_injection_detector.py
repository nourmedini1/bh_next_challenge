from typing import Dict
from skills.prompt_injection_detection.llm_analysis import LLMAnalyzer
from skills.prompt_injection_detection.rule_based_detection import RuleBasedDetector
from a2a.types import AgentSkill

class PromptInjectionDetector: 

    def __init__(
            self, llm_analysis_threshold : float = 0.8, 
            rule_based_detection_threshold: float = 0.35, 
            doubt_threshold: float = 0.2,
            llm_api_key: str = None,
            llm_model_name: str = "mistal-small-latest"
            ):
        self.llm_analysis_threshold = llm_analysis_threshold
        self.rule_based_detection_threshold = rule_based_detection_threshold
        self.doubt_threshold = doubt_threshold
        self.llm_analyzer = LLMAnalyzer(llm_threshold=self.llm_analysis_threshold, api_key=llm_api_key, llm_model_name=llm_model_name)
        self.rule_based_detector = RuleBasedDetector(threshold=self.rule_based_detection_threshold)
        self.skill = AgentSkill(
            id="prompt_injection_detector",
            name="PromptInjectionDetector",
            description="Detect prompt injection attempts in attachment files using rule-based and LLM analysis",
            tags= ["prompt-injection", "attachment", "security", "file-upload"],
            examples=[
                "Detecting prompt injection in a user-uploaded document",
                "Identifying suspicious patterns in attachment metadata"
            ],
            input_modes=[
                "text",
                "file"
            ],
            output_modes=[
                "json",
                "text"
            ],
        )


    def invoke(self, file_content: bytes) -> Dict : 
        file_text = file_content.decode("utf-8")
        detection_result = self.rule_based_detector.detect(file_text)
        score = detection_result.get("score", 0)
        if score < self.rule_based_detection_threshold and score > self.doubt_threshold : 
            llm_score, _ = self.llm_analyzer.analyze_segments(detection_result["matches"])
            if llm_score > self.llm_analysis_threshold:
                detection_result["is_injection"] = True
            detection_result["score"] = llm_score
        return detection_result

