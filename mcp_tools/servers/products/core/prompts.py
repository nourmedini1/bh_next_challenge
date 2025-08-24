from langchain.prompts import ChatPromptTemplate

class Prompts : 

    @staticmethod
    def get_category_prompt() -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """You are an insurance expert assistant. Based on the user's query, 
    identify the most relevant top-level insurance categories and sub-categories from this list:
    
    Categories: {categories}
    
    IMPORTANT INSTRUCTION: When you are uncertain about which category best fits the query,
    always default to including "RISQUES DIVERS" in your selection.
    
    FORMAT INSTRUCTIONS:
    - Return ONLY a JSON array with no additional text, explanation, or formatting
    - Do NOT use markdown code blocks, backticks, or any other formatting
    - The response should be ONLY the raw JSON object itself
    - Example of correct response format: {{"categories": ["VIE", "RISQUES DIVERS"]}}"""),
            ("user", "{query}")
        ])

    @staticmethod
    def get_subcategory_prompt() -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """You are an insurance expert assistant. Based on the user's query and the previously 
    identified insurance categories, select the most relevant sub-categories for each category.

    Available sub-categories for each selected category:
    {sub_categories_by_category}

    IMPORTANT INSTRUCTIONS: 
    1. For each category, select the most relevant sub-categories that match the user's query
    2. When uncertain about which sub-categories best fit, include general sub-categories 
       or those that cover multiple scenarios
    3. If no sub-category seems relevant, include at least one per category

    FORMAT INSTRUCTIONS:
    - Return ONLY a JSON object with no additional text, explanation, or formatting
    - Do NOT use markdown code blocks, backticks, or any other formatting
    - The response should be ONLY the raw JSON object itself
    - Example of correct response format: 
    {{"CATEGORY1": ["SUB_CATEGORY1", "SUB_CATEGORY2"], "CATEGORY2": ["SUB_CATEGORY3"]}}"""),
            ("user", "Query: {query}\n\nIdentified Categories: {identified_categories}")
        ])
    

    @staticmethod
    def get_product_prompt() -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """You are an insurance expert assistant. Based on the user's query and previously 
    identified categories and subcategories, select the most relevant insurance products.

    Available products for each subcategory:
    {products_by_subcategory}

    IMPORTANT INSTRUCTIONS: 
    1. For each subcategory, select only the products that are truly relevant to the user's query
    2. When uncertain about which products best fit, prioritize products with broader coverage
    3. If no specific product seems relevant, include at least one general product per subcategory
    4. Consider user demographics, specific needs, and any constraints mentioned

    FORMAT INSTRUCTIONS:
    - Return ONLY a JSON object with no additional text, explanation, or formatting
    - Do NOT use markdown code blocks, backticks, or any other formatting
    - The response should be ONLY the raw JSON object itself
    - Each key should be a subcategory name and its value should be an array of product names
    - Example of correct response format: 
    {{"SUBCATEGORY1": ["PRODUCT1", "PRODUCT2"], "SUBCATEGORY2": ["PRODUCT3"]}}"""),
            ("user", "Query: {query}\n\nIdentified Categories and Subcategories: {identified_subcategories}")
        ])

