import os
import time
import docker
import psycopg2
import pandas as pd
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# Configurations
DB_CONFIG = {
    "dbname": "insurance_db",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5433,  # host port
}
CONTAINER_NAME = "insurance_pg_container"
POSTGRES_IMAGE = "postgres:15"
EXCEL_FILE = "Données_Assurance_S1.2_S2.2.xlsx"

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DEFAULT_PASSWORD = "12345678"

# Schema SQL
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS accounts (
    ref_personne INT PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    role VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS personne_physique (
    ref_personne INT PRIMARY KEY REFERENCES accounts(ref_personne),
    nom_prenom TEXT,
    date_naissance DATE,
    lieu_naissance TEXT,
    code_sexe VARCHAR(10),
    situation_familiale VARCHAR(100),
    num_piece_identite VARCHAR(50),
    lib_secteur_activite TEXT,
    lib_profession TEXT,
    ville VARCHAR(100),
    lib_gouvernorat VARCHAR(100),
    ville_gouvernorat TEXT
);

CREATE TABLE IF NOT EXISTS personne_morale (
    ref_personne INT PRIMARY KEY REFERENCES accounts(ref_personne),
    raison_sociale TEXT,
    matricule_fiscale VARCHAR(100),
    lib_secteur_activite TEXT,
    lib_activite TEXT,
    ville VARCHAR(100),
    lib_gouvernorat VARCHAR(100),
    ville_gouvernorat TEXT
);

CREATE TABLE IF NOT EXISTS contrats (
    num_contrat VARCHAR(50) PRIMARY KEY,
    ref_personne INT NOT NULL REFERENCES accounts(ref_personne),
    lib_produit TEXT,
    effet_contrat DATE,
    date_expiration DATE,
    prochain_terme VARCHAR(100),
    lib_etat_contrat VARCHAR(100),
    branche VARCHAR(100),
    somme_quittances NUMERIC,
    statut_paiement VARCHAR(50),
    capital_assure NUMERIC
);

CREATE TABLE IF NOT EXISTS garantie_contrat (
    num_contrat VARCHAR(50) REFERENCES contrats(num_contrat),
    code_garantie INT,
    capital_assure NUMERIC,
    lib_garantie TEXT
);

CREATE TABLE IF NOT EXISTS sinistres (
    num_sinistre VARCHAR(50) PRIMARY KEY,
    num_contrat VARCHAR(50) NOT NULL REFERENCES contrats(num_contrat),
    lib_branche VARCHAR(100),
    lib_sous_branche VARCHAR(100),
    lib_produit TEXT,
    nature_sinistre VARCHAR(100),
    lib_type_sinistre VARCHAR(100),
    taux_responsabilite NUMERIC,
    date_survenance DATE,
    date_declaration DATE,
    date_ouverture DATE,
    observation_sinistre TEXT,
    lib_etat_sinistre VARCHAR(100),
    lieu_accident TEXT,
    motif_reouverture TEXT,
    montant_encaisse NUMERIC,
    montant_a_encaisser NUMERIC
);
"""

def wait_for_postgres(host, port, user, password, dbname, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            conn = psycopg2.connect(
                dbname=dbname, user=user, password=password, host=host, port=port
            )
            conn.close()
            print("Postgres is ready!")
            return
        except Exception:
            print("Waiting for Postgres to be ready...")
            time.sleep(2)
    raise TimeoutError("Postgres did not start in time.")

def create_schema(engine):
    with engine.connect() as conn:
        for stmt in SCHEMA_SQL.strip().split(";"):
            if stmt.strip():
                conn.execute(text(stmt))
        conn.commit()

def clean_ref(ref):
    """Ensure ref_personne is always an int"""
    return int(str(ref).strip().replace(".0", ""))

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def generate_email(nom_prenom, ref_personne):
    """Generate email from nom_prenom or use ref_personne as fallback"""
    if pd.isna(nom_prenom) or not nom_prenom:
        return f"user{ref_personne}@gmail.com"
    
    # Clean the name and create email
    name = str(nom_prenom).strip().lower()
    # Replace spaces and special characters with dots
    name = name.replace(" ", ".").replace("'", "").replace("-", ".")
    # Remove any other special characters
    import re
    name = re.sub(r'[^a-z0-9.]', '', name)
    # Remove consecutive dots
    name = re.sub(r'\.+', '.', name)
    # Remove leading/trailing dots
    name = name.strip('.')
    
    return f"{name}@gmail.com"

def insert_accounts(engine, xls):
    accounts = []

    # Mapping: sheet name → role
    role_mapping = {
        "personne_physique": "physique",
        "personne_morale": "morale",
        # Note: Intermédiaires and Compagnie Assurance sheets don't exist in Excel
    }
    hashed_password = hash_password(DEFAULT_PASSWORD)
    for sheet, role in role_mapping.items():
        if sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet)

            if "REF_PERSONNE" in df.columns:
                for index, row in df.iterrows():
                    try:
                        ref_clean = clean_ref(row["REF_PERSONNE"])
                        
                        # Get name for email generation
                        if role == "physique" and "NOM_PRENOM" in df.columns:
                            nom_prenom = row.get("NOM_PRENOM", "")
                        elif role == "morale" and "RAISON_SOCIALE" in df.columns:
                            nom_prenom = row.get("RAISON_SOCIALE", "")
                        else:
                            nom_prenom = ""
                        
                        # Generate email and hash password
                        email = generate_email(nom_prenom, ref_clean)
                        password_hash = hashed_password
                        
                        accounts.append({
                            "ref_personne": ref_clean,
                            "email": email,
                            "password_hash": password_hash,
                            "role": role
                        })
                    except Exception as e:
                        print(f"WARNING: Skipping invalid REF_PERSONNE {row.get('REF_PERSONNE', 'N/A')}: {e}")

    # Drop duplicates on ref_personne
    accounts_df = pd.DataFrame(accounts).drop_duplicates(subset=["ref_personne"])
    accounts_df.to_sql("accounts", engine, if_exists="append", index=False)
    print(f"Inserted {len(accounts_df)} accounts with emails and hashed passwords")

def insert_data(engine, excel_file):
    xls = pd.ExcelFile(excel_file)

    # 1️⃣ Insert into accounts first
    insert_accounts(engine, xls)

    # Fetch valid account IDs (to enforce FK)
    with engine.connect() as conn:
        valid_refs = pd.read_sql("SELECT ref_personne FROM accounts", conn)
    valid_ids = set(valid_refs["ref_personne"].tolist())

    # 2️⃣ Insert into personne_physique
    if "personne_physique" in xls.sheet_names:
        df = pd.read_excel(xls, "personne_physique")
        df = df.rename(columns={
            "REF_PERSONNE": "ref_personne",
            "NOM_PRENOM": "nom_prenom",
            "DATE_NAISSANCE": "date_naissance",
            "LIEU_NAISSANCE": "lieu_naissance",
            "CODE_SEXE": "code_sexe",
            "SITUATION_FAMILIALE": "situation_familiale",
            "NUM_PIECE_IDENTITE": "num_piece_identite",
            "LIB_SECTEUR_ACTIVITE": "lib_secteur_activite",
            "LIB_PROFESSION": "lib_profession",
            "VILLE": "ville",
            "LIB_GOUVERNORAT": "lib_gouvernorat",
            "VILLE_GOUVERNORAT": "ville_gouvernorat",
        })
        df["ref_personne"] = df["ref_personne"].apply(clean_ref)
        df = df[df["ref_personne"].isin(valid_ids)]
        df.to_sql("personne_physique", engine, if_exists="append", index=False)
        print(f"Inserted {len(df)} personne_physique")

    # 3️⃣ Insert into personne_morale
    if "personne_morale" in xls.sheet_names:
        df = pd.read_excel(xls, "personne_morale")
        df = df.rename(columns={
            "REF_PERSONNE": "ref_personne",
            "RAISON_SOCIALE": "raison_sociale",
            "MATRICULE_FISCALE": "matricule_fiscale",
            "LIB_SECTEUR_ACTIVITE": "lib_secteur_activite",
            "LIB_ACTIVITE": "lib_activite",
            "VILLE": "ville",
            "LIB_GOUVERNORAT": "lib_gouvernorat",
            "VILLE_GOUVERNORAT": "ville_gouvernorat",
        })
        df["ref_personne"] = df["ref_personne"].apply(clean_ref)
        df = df[df["ref_personne"].isin(valid_ids)]
        df.to_sql("personne_morale", engine, if_exists="append", index=False)
        print(f"Inserted {len(df)} personne_morale")

    # 4️⃣ Insert into contrats
    if "Contrats" in xls.sheet_names:
        df = pd.read_excel(xls, "Contrats")
        df = df.rename(columns={
            "REF_PERSONNE": "ref_personne",
            "NUM_CONTRAT": "num_contrat",
            "LIB_PRODUIT": "lib_produit",
            "EFFET_CONTRAT": "effet_contrat",
            "DATE_EXPIRATION": "date_expiration",
            "PROCHAIN_TERME": "prochain_terme",
            "LIB_ETAT_CONTRAT": "lib_etat_contrat",
            "branche": "branche",  # already lowercase
            "somme_quittances": "somme_quittances",  # already lowercase
            "statut_paiement": "statut_paiement",  # already lowercase
            "Capital_assure": "capital_assure",
        })
        df["ref_personne"] = df["ref_personne"].apply(clean_ref)
        df = df[df["ref_personne"].isin(valid_ids)]
        # Normalize contract numbers to strings
        df["num_contrat"] = df["num_contrat"].astype(str)
        df.to_sql("contrats", engine, if_exists="append", index=False)
        print(f"Inserted {len(df)} contrats")

    # 5️⃣ Insert into garantie_contrat
    if "Garantie_contrat" in xls.sheet_names:
        df = pd.read_excel(xls, "Garantie_contrat")
        df = df.rename(columns={
            "NUM_CONTRAT": "num_contrat",
            "CODE_GARANTIE": "code_garantie",
            "CAPITAL_ASSURE": "capital_assure",
            "LIB_GARANTIE": "lib_garantie",
        })
        
        # Get valid contract numbers from the contrats table
        with engine.connect() as conn:
            valid_contracts = pd.read_sql("SELECT num_contrat FROM contrats", conn)
        valid_contract_nums = set(valid_contracts["num_contrat"].astype(str).tolist())
        
        # Filter garantie_contrat to only include valid contract numbers
        original_count = len(df)
        df["num_contrat"] = df["num_contrat"].astype(str)  # Normalize to string
        
        # Show example of invalid reference if any exist
        invalid_contracts = df[~df["num_contrat"].isin(valid_contract_nums)]
        if len(invalid_contracts) > 0:
            example_invalid = invalid_contracts["num_contrat"].iloc[0]
            print(f"WARNING: Example invalid contract reference: {example_invalid}")
        
        df = df[df["num_contrat"].isin(valid_contract_nums)]
        filtered_count = len(df)
        
        df.to_sql("garantie_contrat", engine, if_exists="append", index=False)
        print(f"Inserted {filtered_count} garantie_contrat (filtered {original_count - filtered_count} invalid references)")

    # 6️⃣ Insert into sinistres
    if "sinistres" in xls.sheet_names:
        df = pd.read_excel(xls, "sinistres")
        df = df.rename(columns={
            "NUM_SINISTRE": "num_sinistre",
            "NUM_CONTRAT": "num_contrat",
            "LIB_BRANCHE": "lib_branche",
            "LIB_SOUS_BRANCHE": "lib_sous_branche",
            "LIB_PRODUIT": "lib_produit",
            "NATURE_SINISTRE": "nature_sinistre",
            "LIB_TYPE_SINISTRE": "lib_type_sinistre",
            "TAUX_RESPONSABILITE": "taux_responsabilite",
            "DATE_SURVENANCE": "date_survenance",
            "DATE_DECLARATION": "date_declaration",
            "DATE_OUVERTURE": "date_ouverture",
            "OBSERVATION_SINISTRE": "observation_sinistre",
            "LIB_ETAT_SINISTRE": "lib_etat_sinistre",
            "LIEU_ACCIDENT": "lieu_accident",
            "MOTIF_REOUVERTURE": "motif_reouverture",
            "MONTANT_ENCAISSE": "montant_encaisse",
            "MONTANT_A_ENCAISSER": "montant_a_encaisser",
        })
        
        # Get fresh valid contract numbers from the database for sinistres
        with engine.connect() as conn:
            valid_contracts_sinistres = pd.read_sql("SELECT num_contrat FROM contrats", conn)
        valid_contract_nums_sinistres = set(valid_contracts_sinistres["num_contrat"].astype(str).tolist())
        
        # Filter sinistres to only include valid contract numbers
        original_count = len(df)
        df["num_contrat"] = df["num_contrat"].astype(str)  # Normalize to string
        
        # Show example of invalid reference if any exist
        invalid_contracts = df[~df["num_contrat"].isin(valid_contract_nums_sinistres)]
        if len(invalid_contracts) > 0:
            example_invalid = invalid_contracts["num_contrat"].iloc[0]
            print(f"WARNING: Example invalid contract reference in sinistres: {example_invalid}")
        
        df = df[df["num_contrat"].isin(valid_contract_nums_sinistres)]
        filtered_count = len(df)
        
        df.to_sql("sinistres", engine, if_exists="append", index=False)
        print(f"Inserted {filtered_count} sinistres (filtered {original_count - filtered_count} invalid references)")

def main():
    client = docker.from_env()

    # Remove old container if exists
    try:
        old = client.containers.get(CONTAINER_NAME)
        print("Removing old container...")
        old.stop()
        old.remove()
    except docker.errors.NotFound:
        pass

    # Run new Postgres container
    container = client.containers.run(
        POSTGRES_IMAGE,
        name=CONTAINER_NAME,
        environment={
            "POSTGRES_PASSWORD": DB_CONFIG["password"],
            "POSTGRES_DB": DB_CONFIG["dbname"],
        },
        ports={"5432/tcp": DB_CONFIG["port"]},  # container 5432 → host 5433
        detach=True,
    )
    print("Postgres container started")

    wait_for_postgres(DB_CONFIG["host"], DB_CONFIG["port"], DB_CONFIG["user"], DB_CONFIG["password"], DB_CONFIG["dbname"])

    # SQLAlchemy engine
    engine_url = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
    engine = create_engine(engine_url)

    # Create schema
    create_schema(engine)

    # Insert data
    insert_data(engine, EXCEL_FILE)

    print("Database created and populated successfully!")

if __name__ == "__main__":
    main()
