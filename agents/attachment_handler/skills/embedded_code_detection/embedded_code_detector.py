import magic
from typing import Dict, Any

from skills.embedded_code_detection.patterns import (
    ALL_PATTERNS, BINARY_HEADERS, ARCHIVE_MIME_TYPES, CATEGORY_SEVERITY
)
from skills.embedded_code_detection.utils import (
    calculate_entropy, analyze_archive, scan_with_patterns, calculate_score
)

from a2a.types import AgentSkill

class EmbeddedCodeDetector:
    def __init__(self, max_compression_ratio: float = 1000, max_nested_archives: int = 5):
        self.max_compression_ratio = max_compression_ratio
        self.max_nested_archives = max_nested_archives
        self.skill = AgentSkill(
            id="embedded_code_detector",
            name="EmbeddedCodeDetector",
            description="Detect embedded code and potential threats in files",
            tags=["embedded-code", "security", "file-upload"],
            examples=[
                "Scanning a document for embedded scripts",
                "Identifying potential malware in uploaded files"
            ],
            input_modes=[
                "file"
            ],
            output_modes=[
                "json",
                "text"
            ]
        )

    
    def detect(self, file_content: bytes) -> Dict[str, Any]:
        result = {
            "is_malicious": False,
            "score": 0.0,
            "detections": [],
            "mime_type": None,
            "file_size": len(file_content),
            "file_info": {}
        }
        
        if not file_content:
            return result
            
        # Determine file type
        try:
            mime = magic.Magic(mime=True)
            result["mime_type"] = mime.from_buffer(file_content)
        except Exception:
            result["mime_type"] = "unknown"
        
        # Check for binary file header signatures
        for header, file_type in BINARY_HEADERS.items():
            if file_content.startswith(header):
                result["file_info"]["detected_header"] = file_type
                break
        
        # Check for archive-based attacks
        if result["mime_type"] in ARCHIVE_MIME_TYPES:
            archive_result = analyze_archive(
                file_content,
                self.max_compression_ratio,
                self.max_nested_archives
            )
            result["detections"].extend(archive_result["detections"])
            result["file_info"]["archive_analysis"] = archive_result["details"]
        
        # Try to decode as text for pattern matching
        try:
            text_content = file_content.decode('utf-8', errors='replace')
            
            # Scan for malicious patterns
            pattern_results = scan_with_patterns(text_content, ALL_PATTERNS, CATEGORY_SEVERITY)
            result["detections"].extend(pattern_results)
            
        except Exception:
            pass
            
        # Check entropy to identify encoded/encrypted content
        result["file_info"]["entropy"] = calculate_entropy(file_content)
        if result["file_info"]["entropy"] > 7.8:
            result["detections"].append({
                "type": "high_entropy",
                "severity": "medium",
                "details": f"High entropy content ({result['file_info']['entropy']:.2f}/8.0) may indicate encryption or obfuscation"
            })
        
        # Calculate final score based on detections
        result["score"] = calculate_score(result["detections"])
        result["is_malicious"] = result["score"] >= 0.5 or any(d["severity"] == "critical" for d in result["detections"])
        
        return result
    
    def invoke(self, file_content: bytes) -> Dict[str, Any]:
        try:
            return self.detect(file_content)
        except Exception as e:
            return {
                "is_malicious": False,
                "score": 0.0,
                "error": str(e),
                "detections": []
            }