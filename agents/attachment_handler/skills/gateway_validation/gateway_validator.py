from typing import Dict
import magic
from a2a.types import AgentSkill

class GatewayValidator:
    def __init__(self, max_allowed_file_size = 10 * 1024 * 1024,
                 allowed_file_types = [
                     "application/msword",                                           # .doc
                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document", # .docx
                     "application/vnd.ms-excel",                                     # .xls
                     "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", # .xlsx
                     "application/vnd.ms-powerpoint",                               # .ppt
                     "application/vnd.openxmlformats-officedocument.presentationml.presentation", # .pptx                     
                     "application/pdf",                                             # .pdf
                     "text/plain",                                                  # .txt
                     "text/csv",                                                    # .csv
                     "text/markdown",                                               # .md
                     "text/x-markdown",                                             # .markdown                   
                     "application/rtf",                                             # .rtf
                     "application/vnd.oasis.opendocument.text",                     # .odt
                     "application/vnd.oasis.opendocument.spreadsheet",              # .ods
                     "application/vnd.oasis.opendocument.presentation"              # .odp
                 ]
                 ):
        self.max_allowed_file_size = max_allowed_file_size
        self.allowed_file_types = allowed_file_types
        self.skill = AgentSkill(
            id="gateway_validator",
            name="GatewayValidator",
            description="Validate file uploads against security policies",
            tags=["file-upload", "security", "validation"],
            examples=[
                "Validating a user-uploaded document",
                "Checking an attachment for compliance"
            ],
            input_modes=[
                "file"
            ],
            output_modes=[
                "json",
                "text"
            ]
        )

    def is_valid_file_size(self, file_size):
        return file_size <= self.max_allowed_file_size

    def is_valid_file_type(self, file_type):
        print(f"Detected file type: {file_type}")
        return file_type in self.allowed_file_types
    
    def detect_file_type(self, file_content):
        try:
            # Use magic.from_buffer directly
            file_type = magic.from_buffer(file_content, mime=True)
            return file_type
        except Exception as e:
            print(f"Error detecting file type: {e}")
            return "application/octet-stream"

    def invoke(self, file_size : int, file_type : str, file_content : bytes) -> Dict : 
        print(f"Invoking GatewayValidator with file_size={file_size}, file_type={file_type}")
        if not self.is_valid_file_size(file_size):
            return {"valid": False, "reason": "Invalid file size"}
        if not self.is_valid_file_type(file_type):
            return {"valid": False, "reason": "Invalid file type"}
        detected_file_type = self.detect_file_type(file_content)
        if not self.is_valid_file_type(detected_file_type):
            return {"valid": False, "reason": f"Detected file type '{detected_file_type}' is not allowed"}

        return {"valid": True, "reason": ""}