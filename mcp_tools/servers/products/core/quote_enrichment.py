import pandas as pd
import json
from typing import Dict, Any, List, Optional


class QuoteEnricher:
    def __init__(self, product_data_path: str):
        self.product_data_path = product_data_path
        self.product_df = pd.read_excel(self.product_data_path)
        self.total_guarantees = 0
        self.matched_guarantees = 0

    def enrich_quote_data(self, quote_data: Dict[str, Any]) -> Dict[str, Any]:
        enriched_data = {"success": True, "products": {}}
        self.total_guarantees = 0
        self.matched_guarantees = 0
        
        applicable_products = self._filter_applicable_products(quote_data)
        
        for product in applicable_products:
            self._process_product(product, enriched_data)
        
        print(f"Total guarantees processed: {self.total_guarantees}")
        print(f"Guarantees with exact matches: {self.matched_guarantees}")
        return enriched_data
    
    def _filter_applicable_products(self, quote_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [product for product in quote_data.get("quotes", []) 
                if product.get("packApplicable", False) and product.get("packDisponible") == "Pack disponible"]
    
    def _process_product(self, product: Dict[str, Any], enriched_data: Dict[str, Any]) -> None:
        product_code = str(product.get("codeProduit", "")).strip()
        
        for guarantee in product.get("garantieCourtierModels", []):
            self._process_guarantee(product_code, guarantee, product, enriched_data)
    
    def _process_guarantee(self, product_code: str, guarantee: Dict[str, Any], 
                          product: Dict[str, Any], enriched_data: Dict[str, Any]) -> None:
        self.total_guarantees += 1
        guarantee_code = str(guarantee.get("codeGarantie", "")).strip()
        guarantee_name = guarantee.get("libGarantie", "").strip()
        
        match = self._find_match(product_code, guarantee_code, guarantee_name)
        if match is None:
            return
            
        self.matched_guarantees += 1
        product_name = self._get_product_name(match, product_code)
        self._ensure_product_exists(product_name, match, product, product_code, enriched_data)
        self._add_guarantee(product_name, guarantee_name, match, guarantee, guarantee_code, enriched_data)
    
    def _find_match(self, product_code: str, guarantee_code: str, guarantee_name: str) -> Optional[pd.Series]:
        matches = self.product_df[
            (self.product_df["CODE_PRODUIT"].astype(str).str.strip() == product_code) & 
            (self.product_df["CODE_GARANTIE"].astype(str).str.strip() == guarantee_code) &
            (self.product_df["LIB_GARANTIE"].str.strip() == guarantee_name)
        ]
        return matches.iloc[0] if not matches.empty else None
    
    def _get_product_name(self, match, product_code: str) -> str:
        product_name = match.get("LIB_PRODUIT", f"Pack {product_code}")
        return f"Pack {product_code}" if pd.isna(product_name) else product_name
    
    def _ensure_product_exists(self, product_name: str, match, product: Dict[str, Any], 
                              product_code: str, enriched_data: Dict[str, Any]) -> None:
        if product_name not in enriched_data["products"]:
            enriched_data["products"][product_name] = {
                "category": match.get("LIB_BRANCHE", "Automobile"),
                "subcategory": match.get("LIB_SOUS_BRANCHE", ""),
                "guarantees": {},
                "monthly_premium": product.get("montantPrimeDivisePar12", 0),
                "annual_premium": product.get("montantTotalPrime", 0),
            }
    
    def _add_guarantee(self, product_name: str, guarantee_name: str, match, 
                      guarantee: Dict[str, Any], guarantee_code: str, 
                      enriched_data: Dict[str, Any]) -> None:
        enriched_data["products"][product_name]["guarantees"][guarantee_name] = {
            "description": match.get("Description", "") if pd.notna(match.get("Description", "")) else "",
            "targeted_profiles": match.get("Profils cibles", "") if pd.notna(match.get("Profils cibles", "")) else "",
            "capital": guarantee.get("capital", "0"),
            "franchise": guarantee.get("codeFranchise", "0%"),
        }


def process_quotes(product_data_path="data/merged_product_data.xlsx", 
                   quote_path="core/quote_response.json", 
                   output_path="core/enriched_quote_data.json"):
    try:
        with open(quote_path, 'r', encoding='utf-8') as file:
            quote_data = json.load(file)
        
        enricher = QuoteEnricher(product_data_path)
        enriched_data = enricher.enrich_quote_data(quote_data)
        
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(enriched_data, file, ensure_ascii=False, indent=2)
        
        print(f"\nSummary:")
        print(f"- Products with exact matches: {len(enriched_data['products'])}")
        print(f"- Guarantees with exact matches: {sum(len(p['guarantees']) for p in enriched_data['products'].values())}")
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    process_quotes()