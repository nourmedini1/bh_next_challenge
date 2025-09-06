import asyncio
import pandas as pd
import json
from langchain_mistralai import ChatMistralAI
from core.prompts import Prompts

class DataExtractor : 
    def __init__(self, model_name : str, api_key : str) -> None:
        self.llm = ChatMistralAI(
            model=model_name,
            temperature=0.1,
            max_tokens=1000,
            api_key=api_key
        )
        self.initialize_data_sources(
            data_path="data/merged_product_data.xlsx", 
            schema_path="data/insurance_hierarchy.json"
            )
        


    def initialize_data_sources(self, data_path : str, schema_path : str) -> None:
        try:
            self.data = pd.read_excel(data_path)
            self.data_schema : dict  = json.loads(open(schema_path).read())
        except Exception as e:
            print(f"Error initializing data sources: {e}")

    async def extract_relevant_categories(self, query : str) -> dict:
        category_chain = Prompts.get_category_prompt() | self.llm
        try:
            identified_categories = await category_chain.ainvoke({"query": query, "categories": self.data_schema.keys()})
            return json.loads(identified_categories.content)["categories"]
        except Exception as e:
            print(f"Error extracting categories: {e}")
            identified_categories = []

    async def extract_relevant_subcategories(self, query: str, categories: list) -> dict:
        """Extract relevant subcategories for each identified category"""
        subcategory_chain = Prompts.get_subcategory_prompt() | self.llm

        subcategories_by_category = {}
        for category in categories:
            if category in self.data_schema:
                subcategories_by_category[category] = list(self.data_schema[category].keys())
        
        try:
            response = await subcategory_chain.ainvoke({
                "query": query, 
                "identified_categories": categories,
                "sub_categories_by_category": json.dumps(subcategories_by_category, indent=2)
            })
            
            return json.loads(response.content)
        except Exception as e:
            print(f"Error extracting subcategories: {e}")
            return subcategories_by_category
        
    async def extract_relevant_products(self, query: str, subcategories: dict) -> dict:
        """Extract relevant products for each identified subcategory"""
        product_chain = Prompts.get_product_prompt() | self.llm
        
        products_by_subcategory = {}
        
        for category, subcats in subcategories.items():
            if category in self.data_schema:
                for subcategory in subcats:
                    if subcategory in self.data_schema[category]:
                        products_by_subcategory[subcategory] = list(self.data_schema[category][subcategory].keys())
        
        try:
            response = await product_chain.ainvoke({
                "query": query, 
                "identified_subcategories": json.dumps(subcategories, indent=2),
                "products_by_subcategory": json.dumps(products_by_subcategory, indent=2)
            })
            
            return json.loads(response.content)
        except Exception as e:
            print(f"Error extracting products: {e}")
            return products_by_subcategory
        

        
    async def get_description_and_targeted_profiles(self, query: str) -> dict:
        """Get product descriptions, targeted profiles, and guarantees based on user query"""
        categories = await self.extract_relevant_categories(query)
        print(f"Selected categories: {categories}")
        
        subcategories = await self.extract_relevant_subcategories(query, categories)
        print(f"Selected subcategories: {subcategories}")
        
        products = await self.extract_relevant_products(query, subcategories)
        print(f"Selected products: {products}")
        
        filtered_df = pd.DataFrame()
        
        for subcategory, product_list in products.items():
            for category in categories:
                if category in self.data_schema and subcategory in self.data_schema[category]:
                    subcategory_filter = self.data["LIB_SOUS_BRANCHE"] == subcategory
                    product_filter = self.data["LIB_PRODUIT"].isin(product_list)
                    
                    combined_filter = subcategory_filter & product_filter
                    
                    filtered_df = pd.concat([filtered_df, self.data[combined_filter]])
        
        product_data = {}
        
        for _, row in filtered_df.iterrows():
            product_name = row["LIB_PRODUIT"]
            guarantee_name = row["LIB_GARANTIE"]
            
            if product_name not in product_data:
                product_data[product_name] = {
                    "category": row["LIB_BRANCHE"],
                    "subcategory": row["LIB_SOUS_BRANCHE"],
                    "guarantees": {}  
                }
            
            product_data[product_name]["guarantees"][guarantee_name] = {
                "description": row["Description"] if pd.notna(row["Description"]) else "",
                "targeted_profiles": row["Profils cibles"] if pd.notna(row["Profils cibles"]) else ""
            }
        
        return product_data
    

    async def process_query(self, query: str) -> dict:
        """Process a user query and return the most relevant insurance products"""
        try:
            product_data = await self.get_description_and_targeted_profiles(query)
            
            if not product_data:
                return {
                    "success": False,
                    "message": "No insurance products found matching your query.",
                    "products": {}
                }
            
            return {
                "success": True,
                "message": "Found relevant insurance products for your query.",
                "products": product_data
            }
            
        except Exception as e:
            print(f"Error processing query: {e}")
            return {
                "success": False,
                "message": f"Error processing your request: {str(e)}",
                "products": {}
            }
    

if __name__ == "__main__":
    extractor = DataExtractor(model_name="mistral-small-latest", api_key="wIUxlrv4SvHiP3VY1PuIHNhBB4IGRcep")
    query = "What are the insurance options for health coverage?"
    result = asyncio.run(extractor.process_query(query))
    print(result)

