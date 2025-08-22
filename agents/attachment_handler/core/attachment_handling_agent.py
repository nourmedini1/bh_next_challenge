
from typing import Dict

from skills.gateway_validation.gateway_validator import GatewayValidator
from skills.malware_scan.malware_scanner import MalwareScanner
from skills.prompt_injection_detection.prompt_injection_detector import PromptInjectionDetector
from skills.embedded_code_detection.embedded_code_detector import EmbeddedCodeDetector

from core.config import AgentConfig
from core.models.file_data import FileData


from a2a.types import AgentCard,AgentCapabilities
import base64


class AttachmentHandler:

    def __init__(self, config: AgentConfig):
        self.config = config  
        self.gateway_validator = GatewayValidator(
            max_allowed_file_size=self.config["max_allowed_file_size"],
            allowed_file_types=self.config["allowed_file_types"]
        )
        self.prompt_injection_detector = PromptInjectionDetector(
            llm_analysis_threshold=self.config["prompt_injection_LLM_threshold"],
            rule_based_detection_threshold=self.config["prompt_injection_RBD_threshold"],
            doubt_threshold=self.config["prompt_injection_doubt_threshold"],
            llm_api_key=self.config["prompt_injection_api_key"],
            llm_model_name=self.config["prompt_injection_model"]
        )

        self.malware_scanner = MalwareScanner(
            host=self.config["host"],
            port=self.config["port"],
            chunk_size=self.config["chunk_size"]
        )

        self.embedded_code_detector = EmbeddedCodeDetector(
            max_compression_ratio=self.config["max_compression_ratio"],
            max_nested_archives=self.config["max_nested_archives"]
        )

        self.skills = [
            self.gateway_validator.skill,
            self.prompt_injection_detector.skill,
            self.malware_scanner.skill,
            self.embedded_code_detector.skill
        ]

        self.agent_card = AgentCard(
            id="attachment_handler",
            name="AttachmentHandler",
            version="1.0.0",
            description="Handle and analyze file attachments for security threats",
            examples=[
                "Handling a user-uploaded document",
                "Scanning a PDF for malware"
            ],
            capabilities= AgentCapabilities(),
            default_input_modes= ["application/json"],
            default_output_modes= ["application/json"],
            skills=self.skills,
            url="http://0.0.0.0:3001/"
        )

    def invoke(self, file_data : FileData) -> Dict:

        file_content = base64.b64decode(file_data["content"])
        print(f"Invoking GatewayValidator with file_size={file_data['size']}, file_type={file_data['declared_type']}")
        gateway_validation_report = self.gateway_validator.invoke(
            file_size=file_data["size"],
            file_type=file_data["declared_type"], 
            file_content=file_content)
        if not gateway_validation_report["valid"]:
            return {"status": "rejected", "details": gateway_validation_report}
        
        prompt_injection_report = self.prompt_injection_detector.invoke(file_content)
        if prompt_injection_report["is_injection"]:
            return {"status": "rejected", "details": prompt_injection_report}
        
        embedded_code_report = self.embedded_code_detector.invoke(file_content)
        if embedded_code_report["is_malicious"]:
            return {"status": "rejected", "details": embedded_code_report}
        
        malware_scan_report = self.malware_scanner.invoke(file_content)
        if malware_scan_report["is_malicious"]:
            return {"status": "rejected", "details": malware_scan_report}
        
        return {"status": "accepted"}
    

  
   