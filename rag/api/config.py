"""
Configuration for vector stores including metadata and descriptions.
"""

from typing import Dict, List

# Vector store configurations with descriptions
VECTOR_STORE_CONFIG = {
    "1-CG-Vie": {
        "name": "Life Insurance Documents",
        "description": "Contains 11 life insurance products including AMALI, ASSUR SENIOR, DHAMEN series, HANA, HORIZON series, RAHMA, and retirement benefits. Use for queries about life insurance, retirement planning, savings products, death benefits, life coverage, and pension plans.",
        "products": [
            "AMALI", 
            "ASSUR SENIOR", 
            "DHAMEN COMPTE", 
            "DHAMEN RETRAITE", 
            "DHAMEN", 
            "HANA", 
            "HORIZON", 
            "HORIZON+", 
            "RAHMA", 
            "TEMPORAIRE DECES EN COUVERTURE DES PRETS", 
            "INDEMNITE DE DEPART A LA RETRAITE"
        ],
        "use_cases": [
            "life insurance",
            "retirement planning", 
            "savings products",
            "death benefits",
            "life coverage",
            "pension plans",
            "senior insurance"
        ]
    },
    "2-CG-Santé": {
        "name": "Health Insurance Documents", 
        "description": "Contains group health insurance documentation (ASSURANCE GROUPE MALADIE). Use for queries about health insurance, medical coverage, group health plans, healthcare benefits, and illness coverage.",
        "products": [
            "ASSURANCE GROUPE MALADIE"
        ],
        "use_cases": [
            "health insurance",
            "medical coverage",
            "group health plans",
            "healthcare benefits",
            "illness coverage"
        ]
    },
    "3-CG-Transport": {
        "name": "Transport & Marine Insurance Documents",
        "description": "Contains 7 transport and marine insurance products covering cargo insurance (air/land/sea transport) and vessel insurance (pleasure boats, fishing boats, commercial ships). Use for queries about transport insurance, marine insurance, cargo coverage, shipping insurance, boat insurance, and vessel protection.",
        "products": [
            "ASSURANCE DES MARCHANDISES TRANSPORTEES PAR VOIE AERIENNE", 
            "ASSURANCE DES MARCHANDISES TRANSPORTEES PAR VOIE TERRESTRE", 
            "ASSURANCE MARITIME SUR CORPS DE PLAISANCE", 
            "ASSURANCE MARITIME SUR FACULTE", 
            "ASSURANCE SUR CORPS DE NAVIRES DE PECHE", 
            "CORPS DE TOUS NAVIRES", 
            "POLICE FRANCAISE CORPS DE TOUS NAVIRES"
        ],
        "use_cases": [
            "transport insurance",
            "marine insurance",
            "cargo coverage",
            "shipping insurance", 
            "boat insurance",
            "vessel protection"
        ]
    },
    "4-CG-IARD": {
        "name": "Property & Casualty Insurance Documents",
        "description": "Contains 16+ property and casualty insurance products covering home insurance, fire, theft, water damage, business interruption, machinery breakdown, IT equipment, liability, professional coverage, and payment card insurance. Use for queries about home insurance, property damage, theft, fire, liability, professional insurance, card insurance, glass breakage, water damage, and business interruption.",
        "products": [
            "ASSURANCE ASSISTANCE DE LA PROTECTION JURIDIQUE", 
            "ASSURANCE BRIS DE GLACES", 
            "ASSURANCE BRIS DE MACHINES", 
            "ASSURANCE CONTRE LE VOL", 
            "ASSURANCE DÉGÂTS DES EAUX", 
            "ASSURANCE INCENDIE", 
            "ASSURANCE INDIVIDUELLE CONTRE LES ACCIDENTS CORPORELS", 
            "ASSURANCE MULTIRISQUES INFORMATIQUE", 
            "ASSURANCE PERTES D_EXPLOITATION APRES INCENDIE", 
            "CARTE YASMINE", 
            "MULTIRISQUE HABITATION", 
            "MULTIRISQUE PROFESSIONNELLE DES COMMERÇANTS ARTISANS ET PRESTATAIRES DE SERVICES", 
            "PERTE D_EXPLOITATION APRES BRIS DE MACHINES", 
            "RESPONSABILITES CIVILES", 
            "CARTE BH GOLD NATIONALE ET INTERNATIONALE"
        ],
        "use_cases": [
            "home insurance",
            "property damage",
            "theft",
            "fire",
            "liability",
            "professional insurance",
            "card insurance",
            "glass breakage",
            "water damage",
            "business interruption"
        ]
    },
    "5-CG-Engineering": {
        "name": "Engineering & Construction Insurance Documents",
        "description": "Contains 4 engineering and construction insurance products covering construction site risks, assembly operations, decennial liability for building projects, and construction equipment. Use for queries about construction insurance, engineering risks, building projects, contractor insurance, construction equipment, and assembly risks.",
        "products": [
            "ASSURANCE TOUS RISQUES MONTAGE", 
            "CONTRAT D_ASSURANCE UNIQUE PAR CHANTIER DE LA RESPONSABILITE DECENNALE DANS LE DOMAINE DE LA CONSTRUCTION", 
            "ENGINS DE CHANTIERS", 
            "TOUS RISQUES CHANTIER"
        ],
        "use_cases": [
            "construction insurance",
            "engineering risks",
            "building projects",
            "contractor insurance",
            "construction equipment",
            "assembly risks"
        ]
    },
    "6-CG-Automobile": {
        "name": "Automobile Insurance Documents",
        "description": "Contains motor vehicle insurance documentation (ASSURANCE DES VEHICULES TERRESTRES A MOTEURS). Use for queries about car insurance, vehicle coverage, auto insurance, and motor vehicle protection.",
        "products": [
            "ASSURANCE DES VEHICULES TERRESTRES A MOTEURS"
        ],
        "use_cases": [
            "car insurance",
            "vehicle coverage",
            "auto insurance",
            "motor vehicle protection"
        ]
    },
    "7-Assurance-BH-Connaissances-Generales": {
        "name": "BH Assurance General Knowledge Documents",
        "description": "Contains comprehensive general knowledge about BH Assurance policies, procedures, and services. Covers definitions, obligations, contracts, Wininti application, KYC processes, regulations, payment methods, claims procedures, exclusions, and special cases. Use for queries about general insurance concepts, BH Assurance procedures, policy management, premium payments, claim declarations, digital services, regulatory compliance, and customer support.",
        "products": [
            "CONNAISSANCES GENERALES BH ASSURANCE"
        ],
        "use_cases": [
            "insurance definitions",
            "policy procedures",
            "Wininti application",
            "KYC processes",
            "premium payments",
            "claims declaration",
            "digital services",
            "regulatory compliance",
            "customer support",
            "general insurance knowledge",
            "BH Assurance procedures",
            "contract management",
            "attestations",
            "exclusions",
            "fraud prevention",
            "PEP regulations"
        ]
    }
}


def get_store_config(store_name: str) -> Dict:
    """Get configuration for a specific vector store."""
    return VECTOR_STORE_CONFIG.get(store_name)


def get_all_store_names() -> List[str]:
    """Get list of all available vector store names."""
    return list(VECTOR_STORE_CONFIG.keys())


def get_store_description(store_name: str) -> str:
    """Get description for a specific vector store."""
    config = get_store_config(store_name)
    return config["description"] if config else ""


def get_store_products(store_name: str) -> List[str]:
    """Get list of products for a specific vector store."""
    config = get_store_config(store_name)
    return config["products"] if config else []
