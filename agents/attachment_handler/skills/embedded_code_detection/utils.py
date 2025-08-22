import io
import math
import zipfile
import re
from typing import Dict, List, Any

def calculate_entropy(data: bytes) -> float:
    """Calculate Shannon entropy of binary data"""
    if not data:
        return 0
        
    byte_counts = {}
    for byte in data:
        byte_counts[byte] = byte_counts.get(byte, 0) + 1
        
    entropy = 0
    for count in byte_counts.values():
        probability = count / len(data)
        entropy -= probability * (math.log(probability) / math.log(2))
        
    return entropy

def is_potential_bomb(content: bytes, max_compression_ratio: float = 1000) -> bool:
    """Check if content might be a decompression bomb"""
    if len(content) < 100:
        return False
    
    # Check for repeating patterns
    sample = content[:1024]
    chunk_size = min(64, len(sample) // 2)
    for i in range(len(sample) - chunk_size):
        chunk = sample[i:i+chunk_size]
        if sample.count(chunk) > 3:
            return True
    
    # For ZIP files, check compression ratio
    if len(content) < 1024*1024 and content.startswith(b'PK'):
        try:
            with io.BytesIO(content) as file_obj:
                with zipfile.ZipFile(file_obj) as zip_file:
                    total_size = sum(info.file_size for info in zip_file.infolist())
                    ratio = total_size / len(content)
                    return ratio > max_compression_ratio
        except:
            pass
            
    return False

def analyze_archive(content: bytes, max_compression_ratio: float = 1000, 
                    max_nested_archives: int = 5) -> Dict[str, Any]:
    """Analyze archive for zip bombs and other attacks"""
    result = {
        "detections": [],
        "details": {
            "compression_ratio": None,
            "num_files": 0,
            "nested_archives": 0,
            "suspicious_files": []
        }
    }
    
    try:
        if content.startswith(b'PK'):
            with io.BytesIO(content) as file_obj:
                try:
                    with zipfile.ZipFile(file_obj) as zip_file:
                        file_list = zip_file.namelist()
                        result["details"]["num_files"] = len(file_list)
                        
                        compressed_size = len(content)
                        uncompressed_size = sum(zip_info.file_size for zip_info in zip_file.infolist())
                        
                        if compressed_size > 0:
                            ratio = uncompressed_size / compressed_size
                            result["details"]["compression_ratio"] = ratio
                            
                            if ratio > max_compression_ratio:
                                result["detections"].append({
                                    "type": "zip_bomb",
                                    "severity": "critical",
                                    "details": f"Extreme compression ratio: {ratio:.2f}:1"
                                })
                        
                        nested_archives = 0
                        for file_name in file_list:
                            lower_name = file_name.lower()
                            
                            if lower_name.endswith(('.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar', '.jar')):
                                nested_archives += 1
                                try:
                                    nested_content = zip_file.read(file_name)
                                    if len(nested_content) > 0 and is_potential_bomb(nested_content, max_compression_ratio):
                                        result["detections"].append({
                                            "type": "nested_zip_bomb",
                                            "severity": "critical",
                                            "details": f"Potential zip bomb in nested archive: {file_name}"
                                        })
                                except Exception:
                                    pass
                            
                            if lower_name.endswith(('.php', '.phtml', '.php5', '.php4', '.php3', '.pht', 
                                                   '.exe', '.dll', '.bat', '.cmd', '.sh', '.pl', '.py',
                                                   '.cgi', '.asp', '.aspx', '.jsp', '.jspx')):
                                result["details"]["suspicious_files"].append(file_name)
                                result["detections"].append({
                                    "type": "suspicious_file",
                                    "severity": "high",
                                    "details": f"Archive contains potentially executable file: {file_name}"
                                })
                                
                        result["details"]["nested_archives"] = nested_archives
                        if nested_archives > max_nested_archives:
                            result["detections"].append({
                                "type": "excessive_nesting",
                                "severity": "high",
                                "details": f"Archive contains {nested_archives} nested archives (max allowed: {max_nested_archives})"
                            })
                            
                except zipfile.BadZipFile:
                    result["detections"].append({
                        "type": "corrupt_archive",
                        "severity": "medium",
                        "details": "Corrupt or invalid ZIP file structure"
                    })
        
        elif any(content.startswith(header) for header in [b'\x1F\x8B', b'BZ', b'\x42\x5A']):
            result["detections"].append({
                "type": "archive_analysis",
                "severity": "medium",
                "details": "TAR/GZIP archive detected - consider sandbox analysis for complete detection"
            })
            
    except Exception:
        result["detections"].append({
            "type": "analysis_error",
            "severity": "medium",
            "details": "Error analyzing archive"
        })
    
    return result

def scan_with_patterns(text_content: str, pattern_groups: Dict[str, List[str]], 
                       category_severity: Dict[str, str]) -> List[Dict]:
    """Scan text with regex patterns"""
    detections = []
    
    for category, patterns in pattern_groups.items():
        default_severity = category_severity.get(category, "medium")
        
        for pattern in patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                match_text = match.group(0)
                if len(match_text) > 100:
                    match_text = match_text[:97] + "..."
                
                # Determine severity level
                severity = default_severity
                
                # Check for special high-severity cases
                if category == "php" and ("exec(" in match_text or "shell_exec(" in match_text):
                    severity = "critical"
                elif category == "command_injection" and "rm -rf" in match_text.lower():
                    severity = "critical"
                
                detections.append({
                    "type": category,
                    "severity": severity,
                    "pattern": pattern,
                    "match": match_text,
                    "position": match.span()
                })
    
    return detections

def calculate_score(detections: List[Dict]) -> float:
    """Calculate maliciousness score based on detections"""
    if not detections:
        return 0.0
        
    score = 0.0
    severity_weights = {"critical": 1.0, "high": 0.8, "medium": 0.5, "low": 0.2}
    
    for detection in detections:
        severity = detection.get("severity", "medium")
        score += severity_weights.get(severity, 0.5)
    
    # Cap score at 1.0
    return min(score, 1.0)