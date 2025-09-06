"""
Pattern definitions for prompt injection detection.
This file contains regex patterns and keyword sets used to identify potential prompt injection attacks.
"""

# Core instruction override patterns
OVERRIDE_PATTERNS = [
    r"(?:ignore|disregard|forget|don'?t follow|bypass|break|overrule)(?:\s+(?:previous|above|earlier|initial|original))?\s+(?:instructions|rules|guidelines|constraints|limitations|restrictions|prompt|directive)",
    r"(?:stop|start|begin|continue)(?:\s+to)?\s+(?:act|behave|function|identify|operate)(?:\s+as|\s+like)?\s+(?:an?|the)",
    r"\b(?:new prompt|prompt override|instructions override|new instructions|system override)\b",
    r"(?:you are|you're|you will be|you must be|be|act as|pretend to be|assume the role of)\s+(?:a|an)",
    r"for this conversation,?\s+(?:override|ignore|forget|disregard|bypass)",
    r"I want you to (?:pretend|imagine|act)",
    
    # French patterns
    r"(?:ignorer|oublier|ne pas suivre|contourner|briser|passer outre)(?:\s+(?:précédent|ci-dessus|antérieur|initial|original))?\s+(?:instructions|règles|directives|contraintes|limitations|restrictions|prompt)",
    r"(?:arrêter|commencer|débuter|continuer)(?:\s+[àa])?\s+(?:agir|fonctionner|vous comporter|vous identifier)(?:\s+comme)?\s+(?:un|une|le|la)",
    r"\b(?:nouvelle instruction|remplacement de prompt|nouvelles règles|contourner le système)\b",
    r"(?:vous êtes|tu es|soyez|agissez comme|prétendez être|assumez le rôle de)\s+(?:un|une)",
]

# Insurance-specific override patterns
INSURANCE_OVERRIDE_PATTERNS = [
    r"(?:ignore|bypass)(?:\s+(?:company|insurance|policy|claim))?\s+(?:guidelines|rules|limitations|restrictions)",
    r"(?:approve|process|authorize)(?:\s+(?:my|this|the))?\s+(?:claim|policy|coverage|payment|refund)(?:\s+regardless|immediately|without)",
    r"(?:provide|tell me|reveal)(?:\s+(?:confidential|private|internal))?\s+(?:information|data|details|rates|discounts)",
    r"(?:customer service|agent|representative|advisor)(?:\s+mode|override|privileges|access)",
    r"without (?:checking|verifying|reviewing) (?:the|my) policy",
    
    # French patterns
    r"(?:ignorer|contourner)(?:\s+(?:compagnie|assurance|police|réclamation))?\s+(?:directives|règles|limitations|restrictions)",
    r"(?:approuver|traiter|autoriser)(?:\s+(?:ma|cette|la))?\s+(?:réclamation|police|couverture|paiement|remboursement)(?:\s+indépendamment|immédiatement|sans)",
    r"(?:fournir|dire|révéler)(?:\s+(?:confidentiel|privé|interne))?\s+(?:information|données|détails|tarifs|remises)",
    r"(?:service client|agent|représentant|conseiller)(?:\s+mode|dérogation|privilèges|accès)",
]

# Terms that might indicate malicious intent
INSURANCE_KEYWORDS = {
    "fraud", "confidential", "override", "access", "backdoor", "unauthorized",
    "fraude", "confidentiel", "contourner", "accès", "non autorisé"
}

# Jailbreak patterns
JAILBREAK_PATTERNS = [
    # English patterns with word boundaries
    r"\b(?:DAN|do anything now)\b",
    r"\bAIM\b(?!\s+to)",
    r"\bSTAN\b",
    r"\bjailbreak\b",
    r"(?:you have no|without any|bypass|avoid|ignore)(?:\s+ethical|moral|legal)?\s+(?:constraints|limitations|restrictions)",
    r"(?:pretend|imagine|role-play|hypothetically)(?:\s+that)?\s+(?:you are|you're|you can|you(?:'re| are) able to|you have)",
    r"(?:ethical|moral|legal)(?:\s+limitations|constraints|guidelines)?\s+(?:don'?t apply|are suspended|aren'?t relevant)",
    
    # French patterns
    r"\b(?:faire n'importe quoi)\b",
    r"(?:vous n'avez pas|sans aucune|contourner|éviter|ignorer)(?:\s+éthique|morale|légale)?\s+(?:contraintes|limitations|restrictions)",
    r"(?:prétendre|imaginer|jeu de rôle|hypothétiquement)(?:\s+que)?\s+(?:vous êtes|tu es|vous pouvez|tu peux|vous êtes capable de)",
    r"mode (?:DAN|AIM|faire n'importe quoi)",
]

# Role-play based injection patterns
ROLEPLAY_PATTERNS = [
    r"(?:pretend|imagine|role-?play|act as if|assume the role)(?:\s+(?:you are|you're|we are|we're))?\s+(?:in|having|during)(?:\s+a)?",
    r"(?:you are|you're) (?:a|an) (?:system|admin|hacker|developer|root|AI|advanced AI)",
    r"(?:this is|in this) (?:a|an) (?:hypothetical|imaginary|fictional) (?:scenario|situation|exercise)",
    
    # French patterns
    r"(?:prétendre|imaginer|jeu de rôle|agir comme si|assumer le rôle)(?:\s+(?:vous êtes|tu es|nous sommes))?\s+(?:dans|avoir|pendant)(?:\s+un|une)?",
    r"(?:vous êtes|tu es) (?:un|une) (?:système|administrateur|hacker|développeur|root)",
]

# Suspicious keywords that indicate potential injection
SUSPICIOUS_KEYWORDS = {
    "system", "prompt", "instruction", "directive", "ignore", "bypass",
    "jailbreak", "override", "backdoor", "exploit", "forget", "disregard",
    "developer", "debug", "confidential", "secret", "token", "api", "credentials",
    "administrator", "privileges", "authorization", "bot", "hacker",
    
    # French keywords
    "système", "instruction", "directive", "ignorer", "contourner",
    "jailbreak", "backdoor", "exploiter", "oublier", "confidentiel", 
    "secret", "jeton", "api", "identifiants", "administrateur", "privilèges"
}

# Data access and breach patterns
DATA_BREACH_PATTERNS = [
    r"(?:provide|give|show|tell)(?:\s+me)?\s+(?:all|other|customer|client|user)(?:'?s)?\s+(?:data|information|details|policies|claims)",
    r"(?:access|obtain|retrieve|get)(?:\s+to)?\s+(?:database|system|internal|private|confidential)\s+(?:records|data|information|files)",
    r"(?:comparison|comparative)(?:\s+purposes?)",  # Often used to request others' data
    r"(?:normally|typically|usually)(?:\s+(?:would|wouldn't|not))(?:\s+be)?\s+(?:covered|allowed|permitted)",
    
    # French patterns
    r"(?:fournir|donner|montrer|dire)(?:\s+moi)?\s+(?:toutes|autres|client|utilisateur)(?:'?s)?\s+(?:données|informations|détails|polices|réclamations)",
    r"(?:accéder|obtenir|récupérer|avoir)(?:\s+[àa])?\s+(?:base de données|système|interne|privé|confidentiel)\s+(?:dossiers|données|informations|fichiers)",
]

# File-specific patterns for attachment handling
FILE_SPECIFIC_PATTERNS = [
    r"<!--.*?-->",  # HTML comments
    r"/\*.*?\*/",   # C-style comments
    r"```.*?```",   # Markdown code blocks
    r"@system",     # System directives
    r"<(?:script|iframe|object).*?>",  # HTML tags that might contain scripts
    r"\[\[.*?\]\]"  # Double bracket notation sometimes used in templates/injections
]

# Format indicators for suspicious segments detection
FORMAT_INDICATORS = [
    {"pattern": r"```", "context": "Code block formatting"},
    {"pattern": r"<!-", "context": "HTML comment"},
    {"pattern": r"<[a-z]+>", "context": "HTML tag"},
    {"pattern": r"/\*", "context": "Code comment block"},
    {"pattern": r"@system", "context": "System directive"},
    {"pattern": r"\n\n", "context": "Multiple line breaks (potential section division)"}
]

# Strong indicator patterns
STRONG_INDICATORS = {
    "override_instructions": r"(?:ignore|disregard).*(?:previous|above).*instructions",
    "privileged_access": r"(?:administrative|special|full) (?:privileges|access|rights)"
}