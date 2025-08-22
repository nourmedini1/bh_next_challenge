from typing import Dict, List, Any

# JavaScript patterns
JS_PATTERNS = [
    r'<\s*script\b[^>]*>(.*?)<\s*/\s*script\s*>',
    r'javascript\s*:\s*([^"\'>;]*)',
    r'on\w+\s*=\s*(["\'])(?:(?!\1).)*?\1',
    r'eval\s*\((.*?)\)',
    r'document\.write\s*\((.*?)\)',
    r'\\x[0-9a-fA-F]{2}',
    r'\\u[0-9a-fA-F]{4}',
    r'String\.fromCharCode\((.*?)\)',
    r'atob\s*\(\s*["\'](.*?)["\']\s*\)',
    r'<\s*img[^>]*src\s*=\s*["\']?\s*data:',
    r'setTimeout\s*\(\s*(.*?)\s*,',
    r'setInterval\s*\(\s*(.*?)\s*,',
    r'new\s+Function\s*\(([^)]*)\)'
]

# PHP patterns
PHP_PATTERNS = [
    r'<\?(?:php|=)(.*?)(?:\?>|$)',
    r'shell_exec\s*\((.*?)\)',
    r'exec\s*\((.*?)\)',
    r'system\s*\((.*?)\)',
    r'passthru\s*\((.*?)\)',
    r'eval\s*\((.*?)\)',
    r'assert\s*\((.*?)\)',
    r'include\s*\((.*?)\)',
    r'require\s*\((.*?)\)',
    r'include_once\s*\((.*?)\)',
    r'require_once\s*\((.*?)\)',
    r'\$_(?:GET|POST|REQUEST|COOKIE|SERVER|FILES)\s*\[',
    r'file_get_contents\s*\((.*?)\)',
    r'fopen\s*\((.*?)\)',
    r'base64_decode\s*\((.*?)\)'
]

# Python patterns
PYTHON_PATTERNS = [
    r'__import__\s*\((.*?)\)',
    r'exec\s*\((.*?)\)',
    r'eval\s*\((.*?)\)',
    r'os\s*\.\s*system\s*\((.*?)\)',
    r'subprocess\s*\.\s*(?:call|run|Popen)\s*\((.*?)\)',
    r'open\s*\((.*?)\)',
    r'pickle\s*\.\s*loads?\s*\((.*?)\)',
    r'yaml\s*\.\s*(?:unsafe_)?loads?\s*\((.*?)\)',
    r'base64\s*\.\s*(?:b64decode|b32decode|b16decode)\s*\((.*?)\)',
    r'getattr\s*\((.*?)\)',
    r'compile\s*\((.*?)\)',
    r'globals\s*\(\)\s*\[\s*[\'"].*?[\'"]\s*\]\s*='
]

# Command injection patterns
CMD_INJECTION_PATTERNS = [
    r'`(.*?)`',
    r'\$\((.*?)\)',
    r';\s*(?:rm|chmod|chown|wget|curl|nc|bash|sh)\s',
    r'\|\s*(?:sh|bash|nc|netcat)\s',
    r'>\s*/etc/(?:passwd|shadow|hosts)',
    r'(?:curl|wget)\s+(?:-O|-o)\s+(?:http|ftp)://',
    r'\benv\b',
    r'\bnc\s+-\w*(?:e|c)\b',
    r'(?:\/bin|\/usr\/bin|\/sbin)\/[\w]+'
]

# SQL Injection patterns
SQL_INJECTION_PATTERNS = [
    r'(?i)(?:UNION|SELECT|INSERT|UPDATE|DELETE|DROP|ALTER)\s+(?:.*?)\s+(?:FROM|INTO|TABLE|DATABASE)',
    r'(?i)(?:--|#|\/\*)\s*(?:AND|OR|SELECT|UNION)',
    r'(?i)(?:AND|OR)\s+\d+=\d+',
    r'(?i)(?:AND|OR)\s+[\'"]\w+[\'"]=[\'"]',
    r"(?i)(?:AND|OR)\s+['\"]?\w+['\"]?\s*IS\s*(?:NOT\s*)?NULL",
    r'(?i)WAITFOR\s+DELAY',
    r'(?i)(?:EXEC|EXECUTE|DECLARE)\s+@',
    r'(?i)SELECT\s+(?:.*?)\s+FROM\s+information_schema',
    r'(?i)(?:CAST|CONVERT)\s*\(',
    r'(?i)(?:;)\s*(?:USE|EXEC)\s+'
]

# XSS patterns
XSS_PATTERNS = [
    r'<\s*(?:script|iframe|object|embed|applet|meta|link)\b[^>]*>',
    r'<\s*(?:img|input|body|svg|xml)\b[^>]*on\w+\s*=',
    r'<\s*svg\b[^>]*>\s*<\s*(?:script|animate|set)\b',
    r'<\s*[a-z]+\b[^>]*\bstyle\s*=\s*["\'][^"\']*\bexpression\s*\(',
    r'<\s*meta\b[^>]*\bcontent\s*=\s*["\'][^"\']*refresh[^"\']*url\s*=',
    r'<\s*form\b[^>]*\baction\s*=\s*["\']?\s*javascript:',
    r'<!--[^>]*-->\s*<\s*script',
    r'data:(?:text|image)/[^;]*;base64,[A-Za-z0-9+/]+=*',
    r'<\s*a\b[^>]*\bhref\s*=\s*["\']?\s*javascript:'
]

# File upload patterns
FILE_UPLOAD_PATTERNS = [
    r'Content-Type:\s*(?:application|image)/[^;\r\n]+;\s*name\s*=\s*["\']?[^"\';\r\n]*\.(?:php|phtml|php\d|pht|py|pl|rb|sh|cgi|asp|aspx|jsp|jspx|exe|dll|bat|cmd|vbs|vbe|js|reg|asis|cdx|shtml)[\s"\']?',
    r'Content-Disposition:.*?filename\s*=\s*["\']?[^"\']*\.(?:php|phtml|php\d|pht|py|pl|rb|sh|cgi|asp|aspx|jsp|jspx|exe|dll|bat|cmd|vbs|vbe|js|reg)[\s"\']?',
    r'GIF\d+[a-zA-Z](?:\s*<\?(?:php)?|\s*<%)',
    r'\%PDF-\d+\.\d+(?:.*?)(?:\s*<\?(?:php)?|\s*<%)',
    r'MZ[\x90\x00]',
    r'JFIF(?:.*?)(?:\s*<\?(?:php)?|\s*<%)',
    r'\bPK\x03\x04'
]

# Shell patterns
SHELL_PATTERNS = [
    r'(?:c99|r57|shell|b374k|weevely|wso|webshell|backdoor)\.(?:php|aspx?|jsp|cgi|pl|py|rb)',
    r'<title>[^<]*(?:shell|backdoor|c99|r57|wso)[^<]*</title>',
    r'uname\s*-a',
    r'(?:/etc/passwd|/etc/shadow|/etc/hosts)',
    r'%s*(?:\$|#|>)\s*',
    r'(?:cmd|powershell|bash|sh|ksh|csh|tcsh|zsh)\s+/c\s+',
    r'(?:cat|tac|head|tail|less|more|grep|find|ls|dir)\s+/',
    r'id\s*;?\s*uname\s*-a'
]

# Binary file headers
BINARY_HEADERS = {
    b'PK\x03\x04': 'zip',
    b'MZ': 'exe',
    b'\x7FELF': 'elf',
    b'%PDF': 'pdf',
    b'\x1F\x8B\x08': 'gzip',
    b'BZh': 'bz2',
    b'\x42\x5A\x68': 'bz2', 
    b'\x00\x61\x73\x6D': 'wasm',
    b'\x7F\x45\x4C\x46': 'elf',
    b'\xCA\xFE\xBA\xBE': 'class',
    b'\xFE\xED\xFA\xCE': 'macho',
    b'\xFE\xED\xFA\xCF': 'macho64',
    b'\x25\x50\x44\x46': 'pdf'
}

# Archive MIME types
ARCHIVE_MIME_TYPES = [
    'application/zip', 
    'application/x-rar-compressed',
    'application/x-tar', 
    'application/gzip',
    'application/x-bzip2',
    'application/x-7z-compressed',
    'application/java-archive'
]

# Category-based severity mapping
CATEGORY_SEVERITY = {
    "shell": "high",
    "command_injection": "high",
    "php": "medium",  # Base severity, specific patterns may override
    "python": "medium",
    "javascript": "medium",
    "sql_injection": "medium",
    "xss": "medium",
    "file_upload": "medium",
    "high_entropy": "medium"
}

# Special case severity overrides
SPECIAL_CASE_SEVERITY = {
    "php_exec": {"pattern": r'exec\(', "severity": "critical"},
    "php_shell_exec": {"pattern": r'shell_exec\(', "severity": "critical"},
    "nested_zip_bomb": {"severity": "critical"},
    "zip_bomb": {"severity": "critical"}
}

# Group all patterns for easy access
ALL_PATTERNS = {
    'javascript': JS_PATTERNS,
    'php': PHP_PATTERNS,
    'python': PYTHON_PATTERNS,
    'command_injection': CMD_INJECTION_PATTERNS,
    'sql_injection': SQL_INJECTION_PATTERNS,
    'xss': XSS_PATTERNS,
    'file_upload': FILE_UPLOAD_PATTERNS,
    'shell': SHELL_PATTERNS
}