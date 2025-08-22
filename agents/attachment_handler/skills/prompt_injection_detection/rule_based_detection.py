import re
from typing import Dict, List, Union
from skills.prompt_injection_detection import pi_patterns


class RuleBasedDetector:
    def __init__(self, threshold: float = 0.35):
        self.threshold = threshold
        self._initialize_patterns()
    
    def _initialize_patterns(self) -> None:
        self.override_patterns = pi_patterns.OVERRIDE_PATTERNS
        self.insurance_override_patterns = pi_patterns.INSURANCE_OVERRIDE_PATTERNS
        self.insurance_keywords = pi_patterns.INSURANCE_KEYWORDS
        self.jailbreak_patterns = pi_patterns.JAILBREAK_PATTERNS
        self.roleplay_patterns = pi_patterns.ROLEPLAY_PATTERNS
        self.suspicious_keywords = pi_patterns.SUSPICIOUS_KEYWORDS
        self.data_breach_patterns = pi_patterns.DATA_BREACH_PATTERNS
        self.file_specific_patterns = pi_patterns.FILE_SPECIFIC_PATTERNS

    def detect(self, text: str) -> Dict[str, Union[bool, float, int, List[Dict]]]:
        text_lower = text.lower()
        score = 0.0
        matches = []
        pattern_types = set()
        
        # explicit override attempts
        for pattern in self.override_patterns:
            if found := re.search(pattern, text_lower, re.IGNORECASE):
                score += 0.3
                match_text = found.group(0)
                context = "Override pattern"
                matches.append(f"{context}: {match_text}")
                pattern_types.add("override")

        # insurance-specific override attempts
        for pattern in self.insurance_override_patterns:
            if found := re.search(pattern, text_lower, re.IGNORECASE):
                score += 0.35
                match_text = found.group(0)
                context = "Insurance override"
                matches.append(f"{context}: {match_text}")
                pattern_types.add("insurance_override")

        # jailbreak attempts
        for pattern in self.jailbreak_patterns:
            if found := re.search(pattern, text_lower, re.IGNORECASE):
                score += 0.35
                match_text = found.group(0)
                context = "Jailbreak pattern"
                matches.append(f"{context}: {match_text}")
                pattern_types.add("jailbreak")
        
        # roleplay-based injections
        for pattern in self.roleplay_patterns:
            if found := re.search(pattern, text_lower, re.IGNORECASE):
                score += 0.25
                match_text = found.group(0)
                context = "Role-play pattern"
                matches.append(f"{context}: {match_text}")
                pattern_types.add("roleplay")
        
        # suspicious keywords
        words = re.findall(r'\b[a-z]+\b', text_lower)
        suspicious_count = sum(1 for word in words if word in self.suspicious_keywords)
        keyword_ratio = suspicious_count / max(len(words), 1) if words else 0
        if keyword_ratio > 0.03:
            score += keyword_ratio * 0.4
            match_text = f"{keyword_ratio:.2f}"
            context = "Suspicious keyword ratio"
            matches.append(f"{context}: {match_text}")
            pattern_types.add("suspicious_keywords")
        
        # insurance-specific keywords
        insurance_count = sum(1 for word in words if word in self.insurance_keywords)
        insurance_ratio = insurance_count / max(len(words), 1) if words else 0
        if insurance_ratio > 0.02:
            score += insurance_ratio * 0.2
            match_text = f"{insurance_ratio:.2f}"
            context = "Suspicious insurance term ratio"
            matches.append(f"{context}: {match_text}")
            pattern_types.add("insurance_keywords")
        
        # data breach attempts
        for pattern in self.data_breach_patterns:
            if found := re.search(pattern, text_lower, re.IGNORECASE):
                score += 0.4
                match_text = found.group(0)
                context = "Data breach attempt"
                matches.append(f"{context}: {match_text}")
                pattern_types.add("data_breach")
        
        # file-specific patterns
        for pattern in self.file_specific_patterns:
            if found := re.search(pattern, text, re.DOTALL | re.IGNORECASE):
                score += 0.25
                match_text = found.group(0)[:30] + "..." if len(found.group(0)) > 30 else found.group(0)
                context = "Suspicious file formatting"
                matches.append(f"{context}: {match_text}")
                pattern_types.add("file_formatting")
        
        # pattern combination
        if len(pattern_types) >= 2:
            combo_bonus = min(0.3, 0.15 * (len(pattern_types) - 1))
            score += combo_bonus
            match_text = f"{combo_bonus:.2f}"
            context = "Pattern combination"
            matches.append(f"{context}: {match_text}")
        
        # checks for strong indicators
        if re.search(r"(?:ignore|disregard).*(?:previous|above).*instructions", text_lower, re.IGNORECASE):
            score += 0.4
            match_text = "Instructions override attempt"
            context = "Strong indicator"
            matches.append(f"{context}: {match_text}")
            
        if re.search(r"(?:administrative|special|full) (?:privileges|access|rights)", text_lower, re.IGNORECASE):
            score += 0.3
            match_text = "Privileged access request"
            context = "Strong indicator"
            matches.append(f"{context}: {match_text}")
        
        score = min(score, 1.0)
        
        is_injection = score >= self.threshold
        
        detection_result = {
            "score": score,
            "threshold": self.threshold,
            "matches": matches
        }
        segments = self._extract_suspicious_segments(text, detection_result)
        
        structured_matches = []
        for segment in segments:
            structured_matches.append({
                "context": segment["context"],
                "match": segment["match"],
                "text": segment["text"]
            })
        
        result = {
            "is_injection": is_injection,
            "score": score,
            "num_matches": len(matches),
            "matches": structured_matches
        }
        
        return result
    
    def _extract_suspicious_segments(self, text: str, detection_result: Dict) -> List[Dict]:
        """Extract segments of text that need deeper analysis"""
        segments = []
        
        if detection_result["matches"]:
            for match in detection_result["matches"]:
                if isinstance(match, str) and ":" in match:
                    context, pattern = match.split(": ", 1) if ": " in match else ("Unknown", match)
                    try:
                        pattern_pos = text.lower().find(pattern.lower())
                        if pattern_pos >= 0:
                            start = max(0, pattern_pos - 200)
                            end = min(len(text), pattern_pos + len(pattern) + 200)
                            segments.append({
                                "text": text[start:end],
                                "match": pattern,
                                "context": context
                            })
                    except:
                        pass
        
        format_indicators = [
            {"pattern": r"```", "context": "Code block formatting"},
            {"pattern": r"<!-", "context": "HTML comment"},
            {"pattern": r"<[a-z]+>", "context": "HTML tag"},
            {"pattern": r"/\*", "context": "Code comment block"},
            {"pattern": r"@system", "context": "System directive"},
            {"pattern": r"\n\n", "context": "Multiple line breaks (potential section division)"}
        ]
        
        for indicator in format_indicators:
            matches = list(re.finditer(indicator["pattern"], text))
            for match in matches:
                start = max(0, match.start() - 100)
                end = min(len(text), match.start() + 300)
                segments.append({
                    "text": text[start:end],
                    "match": match.group(0),
                    "context": indicator["context"]
                })
        
        if 0.2 <= detection_result["score"] < self.threshold and not segments:
            segments.append({
                "text": text[:min(len(text), 500)],
                "match": "borderline score",
                "context": "Borderline rule score"
            })
        
        # deduplicate segments with high overlap
        filtered_segments = []
        for segment in segments:
            if not any(self._calculate_overlap(segment["text"], fs["text"]) > 0.7 for fs in filtered_segments):
                filtered_segments.append(segment)
        
        return filtered_segments
    
    def _calculate_overlap(self, text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0
        shorter, longer = (text1, text2) if len(text1) <= len(text2) else (text2, text1)
        return sum(1 for c in shorter if c in longer) / len(shorter)
        
    def extract_suspicious_segments(self, text: str, detection_result: Dict) -> List[Dict]:
        return self._extract_suspicious_segments(text, detection_result)