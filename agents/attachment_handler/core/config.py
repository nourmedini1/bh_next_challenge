
from typing import TypedDict


class AgentConfig(TypedDict):
    # Embedded Code Detector Config Params
    max_compression_ratio: float = 1000.0
    max_nested_archives: int = 5

    # Gateway Validator Config Params
    max_allowed_file_size: int = 10485760 # 10 MB
    allowed_file_types: list[str] = [
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
    ]

    # Malware Scanner Config Params
    host: str = "localhost"
    port: int = 3310
    chunk_size: int = 4096

    # Prompt Injection Detection Config Params
    prompt_injection_model: str = "mistral-small-latest"
    prompt_injection_api_key: str = None
    prompt_injection_RBD_threshold: float = 0.35
    prompt_injection_LLM_threshold: float = 0.8
    prompt_injection_doubt_threshold: float = 0.2
