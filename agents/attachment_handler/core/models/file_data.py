


from typing import TypedDict


class FileData(TypedDict) : 
    name: str
    size: int
    declared_type: str
    content: str  # base64 encoded content
