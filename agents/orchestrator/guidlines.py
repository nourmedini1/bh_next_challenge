import parlant.sdk as p
import tools.rag_tool as rag_tools
import tools.database_access_tool as database_tools
from tools.mcp_products_tool import get_non_automobile_insurance_products_descriptions
from tools.mcp_quotes_tool import get_automobile_insurance_quote

async def create_guidelines(agent: p.Agent):

    await agent.create_guideline(
        condition="User query is written in Arabic language.",
        action="""
        1. First, translate the Arabic query to French to understand the user's request.
        2. Process the translated French query using the appropriate insurance category guidelines.
        3. ALWAYS respond to the user in Arabic, providing the information they requested.
        4. Maintain the same level of detail and accuracy as you would for French queries.
        5. All responses must be in Arabic language - never respond in French or English when the user wrote in Arabic.
        """,
        tools=[]
    )

    # --- Automobile Insurance Information (Exclusive to vehicle-related queries) ---
    await agent.create_guideline(
        condition="User specifically asks about automobile insurance coverage, policies, or products related to ASSURANCE DES VEHICULES TERRESTRES A MOTEURS, without mentioning other insurance categories like life, health, transport, property, engineering, or general concepts, and is NOT requesting a quote or cost estimate.",
        action="""
        1. Use search_automobile_insurance_documents with a precise query focused only on the user's specific automobile-related question to retrieve coverage details.
        2. Summarize only the relevant aspects: liability, collision, comprehensive, and exclusions. Do not include information from other insurance categories.
        3. If the user seems interested in pricing, mention that you can help them get a personalized quote if they'd like.
        """,
        tools=[rag_tools.search_automobile_insurance_documents]
    )

    # --- Automobile Insurance Quote Generation (Exclusive to quote requests) ---
    await agent.create_guideline(
        condition="User specifically requests a quote, cost estimate, or pricing for automobile insurance, or expresses interest in getting a personalized quote for vehicle insurance.",
        action="""
        1. Collect all required information systematically by asking for:
           - n_cin: National ID number of the vehicle owner
           - valeur_venale: Current market value of the vehicle in currency units
           - nature_contrat: Contract type ('r' for civil responsibility and liability , 'n' for all risks (comprehensive))
           - nombre_place: Number of seats in the vehicle
           - valeur_a_neuf: Value of the vehicle when new in currency units
           - date_premiere_mise_en_circulation: Date of first registration in YYYY-MM-DD format
           - capital_bris_de_glace: Glass breakage coverage amount
           - capital_dommage_collision: Collision damage coverage amount
           - puissance: Vehicle engine power
           - classe: Vehicle class category
        2. Verify that no required data is missing before proceeding. Ask for any missing information clearly.
        3. Once all data is collected and verified, use get_automobile_insurance_quote to generate the quote.
        4. Present the quote results in detail, explaining:
           - Available insurance packages and options
           - Prices amounts (monthly and annual) in Tunisian Dinar TND
           - Coverage details and limits
           - Applicable guarantees and exclusions
           - Next steps for purchasing or modifying the quote
        5. Do not trigger any other tools or provide unrelated insurance information.
        """,
        tools=[get_automobile_insurance_quote]
    )

    # --- Life Insurance (Exclusive to life, retirement, and specific products) ---
    await agent.create_guideline(
        condition="User specifically asks about life insurance, retirement plans, savings products, death benefits, senior insurance, or the exact products: AMALI, ASSUR SENIOR, DHAMEN, HANA, HORIZON, RAHMA, TEMPORAIRE DECES, INDEMNITE DE DEPART, without mentioning other insurance categories like automobile, health, transport, property, engineering, or general concepts.",
        action="""
        1. Use search_life_insurance_documents with a precise query limited to the user's specific life insurance question to retrieve details.
        2. Summarize only the relevant coverage, savings/retirement aspects, and exclusions for the mentioned products. Do not expand to unrelated products or categories.
        3. Highlight key benefits only for the explicitly mentioned products.
        """,
        tools=[rag_tools.search_life_insurance_documents]
    )

    # --- Health Insurance (Exclusive to health and group plans) ---
    await agent.create_guideline(
        condition="User specifically asks about health insurance, group health plans, medical coverage, illness coverage, or the exact product ASSURANCE GROUPE MALADIE, without mentioning other insurance categories like automobile, life, transport, property, engineering, or general concepts.",
        action="""
        1. Use search_health_insurance_documents with a precise query focused on the user's specific health-related question to retrieve coverage and eligibility details.
        2. Present only the relevant benefits such as hospitalization, medical expenses, and illness coverage.
        3. Use get_non_automobile_insurance_products_descriptions only if the user asks for a detailed product description beyond basic coverage; otherwise, skip this tool.
        """,
        tools=[rag_tools.search_health_insurance_documents, get_non_automobile_insurance_products_descriptions]
    )

    # --- Transport & Marine Insurance (Exclusive to transport/marine topics) ---
    await agent.create_guideline(
        condition="User specifically asks about transport, marine, cargo, boat, or vessel insurance, or the exact products: ASSURANCE MARCHANDISES (air/land/sea), CORPS DE NAVIRE, PLAISANCE, PECHE, without mentioning other insurance categories like automobile, life, health, property, engineering, or general concepts.",
        action="""
        1. Use search_transport_marine_documents with a precise query limited to the user's specific transport/marine question to retrieve details.
        2. Explain only cargo vs vessel coverage, conditions, and exclusions relevant to the query.
        3. Use get_non_automobile_insurance_products_descriptions only if the user requests a full product description; otherwise, skip this tool.
        """,
        tools=[rag_tools.search_transport_marine_documents, get_non_automobile_insurance_products_descriptions]
    )

    # --- Property & Casualty Insurance (Exclusive to property/casualty topics) ---
    await agent.create_guideline(
        condition="User specifically asks about home insurance, theft, fire, water damage, liability, professional coverage, card insurance, or the exact products: MULTIRISQUE HABITATION, PROFESSIONNELLE, CARTE YASMINE, CARTE BH GOLD, INCENDIE, VOL, DEGATS DES EAUX, MACHINES, INFORMATIQUE, without mentioning other insurance categories like automobile, life, health, transport, engineering, or general concepts.",
        action="""
        1. Use search_property_casualty_documents with a precise query focused on the user's specific property/casualty question to retrieve details.
        2. Distinguish only the relevant types: personal (home) vs professional (business) vs specific risks, based on the query.
        3. Summarize inclusions and exclusions only for the mentioned aspects.
        4. Use get_non_automobile_insurance_products_descriptions only if the user asks for a detailed product overview; otherwise, skip this tool.
        """,
        tools=[rag_tools.search_property_casualty_documents, get_non_automobile_insurance_products_descriptions]
    )

    # --- Engineering & Construction Insurance (Exclusive to engineering/construction topics) ---
    await agent.create_guideline(
        condition="User specifically asks about construction, engineering, contractor, equipment, or assembly risks, or the exact products: TOUS RISQUES CHANTIER, TOUS RISQUES MONTAGE, RESPONSABILITE DECENNALE, ENGINS DE CHANTIERS, without mentioning other insurance categories like automobile, life, health, transport, property, or general concepts.",
        action="""
        1. Use search_engineering_construction_documents with a precise query limited to the user's specific engineering/construction question to retrieve details.
        2. Summarize only the relevant coverage: site risks, assembly, decennial liability, equipment.
        3. Use get_non_automobile_insurance_products_descriptions only if the user requests a complete product description; otherwise, skip this tool.
        """,
        tools=[rag_tools.search_engineering_construction_documents, get_non_automobile_insurance_products_descriptions]
    )

    # --- General Knowledge (Fallback for non-category-specific queries) ---
    await agent.create_guideline(
        condition="User asks about general insurance concepts, BH Assurance procedures, claims processes, Wininti, KYC, payments, attestations, exclusions, fraud, or regulations, without referencing specific insurance categories like automobile, life, health, transport, property, or engineering.",
        action="""
        1. Use search_general_knowledge_documents with a precise query targeted at the user's specific general question to retrieve relevant info.
        2. Present a clear explanation or step-by-step process only for the queried topic. Do not trigger any category-specific tools.
        """,
        tools=[rag_tools.search_general_knowledge_documents]
    )

    # --- Guest User Data Access (Strict check for guest status) ---
    await agent.create_guideline(
        condition="User asks about their personal data from the database (e.g., personal info, contracts, claims) and they are currently a guest (not logged in).",
        action="""
        1. Politely inform the user that they need to log in to access their data. Do not call any tools or proceed further.
        """,
        tools=[]
    )

    # --- User Personal Info (Only when explicitly needed and user is logged in) ---
    await agent.create_guideline(
        condition="The agent explicitly needs user personal info (name, profession, email, address, national ID) for a task, and the user is logged in. Do not trigger for general queries.",
        action="""
        1. Use get_complete_user_info to lookup and return only the required user info. Do not fetch unnecessary data.
        """,
        tools=[database_tools.get_complete_user_info]
    )

    # --- Claims Assistance (Exclusive to claims queries, user logged in) ---
    await agent.create_guideline(
        condition="User specifically asks for claim assistance or details about their claims, and the user is logged in. Do not trigger for other data requests.",
        action="""
        1. If the user provides a specific claim number, use get_claim_details with that number only.
        2. If no claim number is provided, use get_user_claims to list all claims briefly.
        3. Present only the claim details clearly. Do not trigger contract or personal info tools.
        """,
        tools=[database_tools.get_claim_details, database_tools.get_user_claims]
    )

    # --- Contracts Information (Exclusive to contracts queries, user logged in) ---
    await agent.create_guideline(
        condition="User specifically asks about their insurance contracts or a specific contract, and the user is logged in. Do not trigger for claims or personal info requests.",
        action="""
        1. If the user provides a specific contract ID, use get_contract_details with that ID only.
        2. If no contract ID is provided, use get_user_contracts to list all contracts briefly.
        3. Present only the contract details clearly. Do not trigger claim or personal info tools.
        """,
        tools=[database_tools.get_contract_details, database_tools.get_user_contracts]
    )