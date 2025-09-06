from pydantic import BaseModel, Field
from typing import Literal

class QuoteRequest(BaseModel):
    """
    Defines the structure for a request to the Hackathon Assurance API.
    Each attribute corresponds to a query parameter.
    """
    n_cin: str = Field(
        ..., 
        description="National ID number of the insured person.",
        example="08478931"
    )
    valeur_venale: int = Field(
        ...,
        description="Current market value of the car (in local currency).",
        example=60000
    )
    nature_contrat: Literal['r', 'n'] = Field(
        ...,
        description="Type of insurance contract: 'r' for Responsabilité Civile (liability) or 'n' for Tous Risques (comprehensive).",
        example="n"
    )
    nombre_place: int = Field(
        ...,
        description="Number of seats in the vehicle.",
        example=5
    )
    valeur_a_neuf: int = Field(
        ...,
        description="Replacement value if the car is brand new.",
        example=60000
    )
    date_premiere_mise_en_circulation: str = Field(
        ...,
        description="Date of first registration of the vehicle.",
        example="2022-02-28"
    )
    capital_bris_de_glace: int = Field(
        ...,
        description="Coverage limit for broken glass (windshield, windows).",
        example=900
    )
    capital_dommage_collision: int = Field(
        ...,
        description="Coverage limit for damage caused by collision.",
        example=60000
    )
    puissance: int = Field(
        ...,
        description="Fiscal horsepower of the car.",
        example=6
    )
    classe: int = Field(
        ...,
        description="Risk/bonus-malus class of the driver.",
        example=3
    )