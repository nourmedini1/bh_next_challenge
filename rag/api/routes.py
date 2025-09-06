"""
FastAPI router for vector store query endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict

from api.models import QueryRequest, QueryResponse, StoreInfo
from api.config import VECTOR_STORE_CONFIG, get_store_config
from api.vector_store_service import VectorStoreService


def get_vector_store_service() -> VectorStoreService:
    """Dependency to get vector store service instance."""
    # This will be injected by the main app
    return vector_store_service


# Global service instance (will be initialized in main app)
vector_store_service: VectorStoreService = None


router = APIRouter(prefix="/query", tags=["Vector Store Queries"])


@router.get("/stores", response_model=Dict[str, StoreInfo])
async def get_stores_info(service: VectorStoreService = Depends(get_vector_store_service)):
    """Get information about all available vector stores."""
    stores_info = {}
    for store_name, config in VECTOR_STORE_CONFIG.items():
        stores_info[store_name] = StoreInfo(
            name=config["name"],
            description=config["description"],
            products=config["products"],
            loaded=service.is_store_loaded(store_name),
            endpoint=f"/query/{store_name}"
        )
    return stores_info


async def _query_vector_store_endpoint(store_name: str, request: QueryRequest, service: VectorStoreService) -> QueryResponse:
    """Helper function to query a specific vector store."""
    try:
        # Query the vector store
        document_results = await service.query_vector_store(store_name, request.query, request.k)
        
        return QueryResponse(
            query=request.query,
            results=document_results,
            total_results=len(document_results),
            vector_store=store_name
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/1-CG-Vie", response_model=QueryResponse)
async def query_life_insurance(
    request: QueryRequest, 
    service: VectorStoreService = Depends(get_vector_store_service)
):
    """
    Query Life Insurance Documents (1-CG-Vie)
    
    Contains 11 life insurance products including AMALI, ASSUR SENIOR, DHAMEN series, HANA, HORIZON series, RAHMA, and retirement benefits.
    Use for queries about: life insurance, retirement planning, savings products, death benefits, life coverage, pension plans, senior insurance.
    
    Products: AMALI, ASSUR SENIOR, DHAMEN COMPTE, DHAMEN RETRAITE, DHAMEN, HANA, HORIZON, HORIZON+, RAHMA, TEMPORAIRE DECES EN COUVERTURE DES PRETS, INDEMNITE DE DEPART A LA RETRAITE
    """
    return await _query_vector_store_endpoint("1-CG-Vie", request, service)


@router.post("/2-CG-Santé", response_model=QueryResponse) 
async def query_health_insurance(
    request: QueryRequest,
    service: VectorStoreService = Depends(get_vector_store_service)
):
    """
    Query Health Insurance Documents (2-CG-Santé)
    
    Contains group health insurance documentation.
    Use for queries about: health insurance, medical coverage, group health plans, healthcare benefits, illness coverage.
    
    Products: ASSURANCE GROUPE MALADIE
    """
    return await _query_vector_store_endpoint("2-CG-Santé", request, service)


@router.post("/3-CG-Transport", response_model=QueryResponse)
async def query_transport_marine_insurance(
    request: QueryRequest,
    service: VectorStoreService = Depends(get_vector_store_service)
):
    """
    Query Transport & Marine Insurance Documents (3-CG-Transport)
    
    Contains 7 transport and marine insurance products covering cargo and vessel insurance.
    Use for queries about: transport insurance, marine insurance, cargo coverage, shipping insurance, boat insurance, vessel protection.
    
    Products: ASSURANCE DES MARCHANDISES TRANSPORTEES (AIR/TERRESTRE), ASSURANCE MARITIME (CORPS DE PLAISANCE/FACULTE), ASSURANCE SUR CORPS DE NAVIRES DE PECHE, CORPS DE TOUS NAVIRES, POLICE FRANCAISE CORPS DE TOUS NAVIRES
    """
    return await _query_vector_store_endpoint("3-CG-Transport", request, service)


@router.post("/4-CG-IARD", response_model=QueryResponse)
async def query_property_casualty_insurance(
    request: QueryRequest,
    service: VectorStoreService = Depends(get_vector_store_service)
):
    """
    Query Property & Casualty Insurance Documents (4-CG-IARD)
    
    Contains 16+ property and casualty insurance products covering comprehensive property and business risks.
    Use for queries about: home insurance, property damage, theft, fire, liability, professional insurance, card insurance, glass breakage, water damage, business interruption.
    
    Products: ASSURANCE ASSISTANCE DE LA PROTECTION JURIDIQUE, BRIS DE GLACES/MACHINES, CONTRE LE VOL, DÉGÂTS DES EAUX, INCENDIE, ACCIDENTS CORPORELS, MULTIRISQUES INFORMATIQUE/HABITATION/PROFESSIONNELLE, PERTES D'EXPLOITATION, CARTE YASMINE/BH GOLD, RESPONSABILITES CIVILES
    """
    return await _query_vector_store_endpoint("4-CG-IARD", request, service)


@router.post("/5-CG-Engineering", response_model=QueryResponse)
async def query_engineering_construction_insurance(
    request: QueryRequest,
    service: VectorStoreService = Depends(get_vector_store_service)
):
    """
    Query Engineering & Construction Insurance Documents (5-CG-Engineering)
    
    Contains 4 engineering and construction insurance products covering construction and assembly risks.
    Use for queries about: construction insurance, engineering risks, building projects, contractor insurance, construction equipment, assembly risks.
    
    Products: ASSURANCE TOUS RISQUES MONTAGE, CONTRAT D_ASSURANCE UNIQUE PAR CHANTIER DE LA RESPONSABILITE DECENNALE, ENGINS DE CHANTIERS, TOUS RISQUES CHANTIER
    """
    return await _query_vector_store_endpoint("5-CG-Engineering", request, service)


@router.post("/6-CG-Automobile", response_model=QueryResponse)
async def query_automobile_insurance(
    request: QueryRequest,
    service: VectorStoreService = Depends(get_vector_store_service)
):
    """
    Query Automobile Insurance Documents (6-CG-Automobile)
    
    Contains motor vehicle insurance documentation.
    Use for queries about: car insurance, vehicle coverage, auto insurance, motor vehicle protection.
    
    Products: ASSURANCE DES VEHICULES TERRESTRES A MOTEURS
    """
    return await _query_vector_store_endpoint("6-CG-Automobile", request, service)


@router.post("/7-Assurance-BH-Connaissances-Generales", response_model=QueryResponse)
async def query_bh_general_knowledge(
    request: QueryRequest,
    service: VectorStoreService = Depends(get_vector_store_service)
):
    """
    Query BH Assurance General Knowledge Documents (7-Assurance-BH-Connaissances-Generales)
    
    Contains comprehensive general knowledge about BH Assurance policies, procedures, and services.
    Covers definitions, obligations, contracts, Wininti application, KYC processes, regulations, payment methods, claims procedures, exclusions, and special cases.
    Use for queries about: insurance definitions, policy procedures, Wininti application, KYC processes, premium payments, claims declaration, digital services, regulatory compliance, customer support, general insurance knowledge, BH Assurance procedures, contract management, attestations, exclusions, fraud prevention, PEP regulations.
    
    Topics covered:
    - General definitions (premium, franchise, etc.)
    - Policy obligations and procedures
    - Wininti mobile application usage
    - KYC (Know Your Customer) processes
    - Regulatory compliance (LAB/FT)
    - Auto insurance basics (RC, damages, theft, assistance)
    - Health insurance (hospitalization, medical care, maternity)
    - Life insurance (death benefits, disability, savings)
    - Home insurance (fire, water damage, theft, liability)
    - Travel insurance (medical, repatriation, baggage)
    - School insurance (accidents, liability)
    - Legal protection insurance
    - Payment methods and procedures
    - Claims declaration and processing
    - Exclusions and special cases
    - Dispute resolution and mediation
    """
    return await _query_vector_store_endpoint("7-Assurance-BH-Connaissances-Generales", request, service)
