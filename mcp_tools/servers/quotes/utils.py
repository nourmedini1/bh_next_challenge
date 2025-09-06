

from core.models.quote_request import QuoteRequest
from typing import Dict, Any
from pydantic import ValidationError
from datetime import datetime
import re



def validate_quote_request(data: Dict[str, Any]) -> Dict[str, Any]:
    errors = []
    required_fields = [
        "n_cin", "valeur_venale", "nature_contrat", "nombre_place",
        "valeur_a_neuf", "date_premiere_mise_en_circulation",
        "capital_bris_de_glace", "capital_dommage_collision",
        "puissance", "classe"
    ]
    
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f"Le champ '{field}' est requis.")
    
    if errors:
        return {"success": False, "errors": errors}
    
    
    if "n_cin" in data:
        if not re.match(r"^\d{8}$", data["n_cin"]):
            errors.append("Le numéro de CIN doit contenir exactement 8 chiffres.")
    
    numeric_fields = {
        "valeur_venale": "La valeur vénale doit être un nombre positif.",
        "nombre_place": "Le nombre de places doit être un nombre positif entre 1 et 9.",
        "valeur_a_neuf": "La valeur à neuf doit être un nombre positif.",
        "capital_bris_de_glace": "Le capital bris de glace doit être un nombre positif.",
        "capital_dommage_collision": "Le capital dommage collision doit être un nombre positif.",
        "puissance": "La puissance fiscale doit être un nombre positif entre 1 et 20.",
        "classe": "La classe doit être un nombre positif entre 1 et 10."
    }
    
    for field, error_msg in numeric_fields.items():
        if field in data:
            try:
                value = int(data[field])
                
                if field == "nombre_place" and (value < 1 or value > 9):
                    errors.append("Le nombre de places doit être entre 1 et 9.")
                elif field == "puissance" and (value < 1 or value > 20):
                    errors.append("La puissance fiscale doit être entre 1 et 20.")
                elif field == "classe" and (value < 1 or value > 10):
                    errors.append("La classe doit être entre 1 et 10.")
                elif value <= 0:
                    errors.append(error_msg)
            except (ValueError, TypeError):
                errors.append(f"Le champ '{field}' doit être un nombre.")
    
    if "nature_contrat" in data:
        if data["nature_contrat"] not in ["r", "n"]:
            errors.append("La nature du contrat doit être 'r' (Responsabilité Civile) ou 'n' (Tous Risques).")
    
    if "date_premiere_mise_en_circulation" in data:
        try:
            date_str = data["date_premiere_mise_en_circulation"]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            
            if date_obj > datetime.now():
                errors.append("La date de première mise en circulation ne peut pas être dans le futur.")
            
            fifty_years_ago = datetime.now().replace(year=datetime.now().year - 50)
            if date_obj < fifty_years_ago:
                errors.append("La date de première mise en circulation semble trop ancienne (plus de 50 ans).")
                
        except ValueError:
            errors.append("Le format de la date doit être AAAA-MM-JJ (exemple: 2022-02-28).")
    
    if "valeur_venale" in data and "valeur_a_neuf" in data:
        try:
            if int(data["valeur_venale"]) > int(data["valeur_a_neuf"]):
                errors.append("La valeur vénale ne peut pas être supérieure à la valeur à neuf.")
        except (ValueError, TypeError):
            pass  
    
    if errors:
        return {"success": False, "errors": errors}
    
    try:
        QuoteRequest(**data)
        return {"success": True}
    except ValidationError as e:
        for error in e.errors():
            errors.append(f"{error['loc'][0]}: {error['msg']}")
        return {"success": False, "errors": errors}
