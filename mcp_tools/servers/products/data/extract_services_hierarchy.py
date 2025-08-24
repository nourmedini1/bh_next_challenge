
import pandas as pd
import json
from pathlib import Path

df = pd.read_excel("merged_product_data.xlsx")


expected_cols = ["LIB_BRANCHE", "LIB_SOUS_BRANCHE", "LIB_PRODUIT", "LIB_GARANTIE"]
df = df[[col for col in expected_cols if col in df.columns]].dropna(how="all")

# Build hierarchical dict
hierarchy = {}

for _, row in df.iterrows():
    branch = row.get("LIB_BRANCHE")
    sous = row.get("LIB_SOUS_BRANCHE")
    product = row.get("LIB_PRODUIT")
    garantie = row.get("LIB_GARANTIE")

    if not branch or not sous or not product or not garantie:
        continue

    # Initialize branch
    if branch not in hierarchy:
        hierarchy[branch] = {}

    # Initialize sous-branch
    if sous not in hierarchy[branch]:
        hierarchy[branch][sous] = {}

    # Initialize product
    if product not in hierarchy[branch][sous]:
        hierarchy[branch][sous][product] = []

    # Add garantie (avoid duplicates)
    if garantie not in hierarchy[branch][sous][product]:
        hierarchy[branch][sous][product].append(garantie)

# Save to JSON
with open("insurance_hierarchy.json", "w", encoding="utf-8") as f:
    json.dump(hierarchy, f, ensure_ascii=False, indent=2)

print(f"Hierarchy JSON saved to: insurance_hierarchy.json")
