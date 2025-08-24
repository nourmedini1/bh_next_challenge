from sqlalchemy import Column, Integer, String, Text, Date, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db.core.database import Base


class Account(Base):
    __tablename__ = "accounts"
    
    ref_personne = Column(Integer, primary_key=True, autoincrement=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(10), nullable=False)  # 'physique' or 'morale'
    
    # Relationships
    personne_physique = relationship("PersonnePhysique", back_populates="account", uselist=False)
    personne_morale = relationship("PersonneMorale", back_populates="account", uselist=False)
    contrats = relationship("Contrat", back_populates="account")


class PersonnePhysique(Base):
    __tablename__ = "personne_physique"
    
    ref_personne = Column(Integer, ForeignKey("accounts.ref_personne"), primary_key=True, autoincrement=False)
    nom_prenom = Column(Text, nullable=False)
    date_naissance = Column(Date)
    lieu_naissance = Column(Text)
    code_sexe = Column(String(1))
    situation_familiale = Column(String(100))
    num_piece_identite = Column(String(50))
    lib_secteur_activite = Column(Text)
    lib_profession = Column(Text)
    ville = Column(String(100))
    lib_gouvernorat = Column(String(100))
    ville_gouvernorat = Column(Text)
    
    # Relationship
    account = relationship("Account", back_populates="personne_physique")


class PersonneMorale(Base):
    __tablename__ = "personne_morale"
    
    ref_personne = Column(Integer, ForeignKey("accounts.ref_personne"), primary_key=True, autoincrement=False)
    raison_sociale = Column(Text, nullable=False)
    matricule_fiscale = Column(String(100))
    num_secteur_activite = Column(Text)
    lib_activite = Column(Text)
    ville = Column(String(100))
    lib_gouvernorat = Column(String(100))
    ville_gouvernorat = Column(Text)
    
    # Relationship
    account = relationship("Account", back_populates="personne_morale")


class GarantieContrat(Base):
    __tablename__ = "garantie_contrat"
    
    num_contrat = Column(String(50), ForeignKey("contrats.num_contrat"), primary_key=True, autoincrement=False)
    code_garantie = Column(Integer, primary_key=True, autoincrement=False)
    lib_garantie = Column(Text)
    
    # Relationship
    contrat = relationship("Contrat", back_populates="garanties")


class Contrat(Base):
    __tablename__ = "contrats"
    
    num_contrat = Column(String(50), primary_key=True, autoincrement=False)
    ref_personne = Column(Integer, ForeignKey("accounts.ref_personne"), nullable=False)
    lib_produit = Column(Text)
    effet_contrat = Column(Date)
    date_expiration = Column(Date)  # Changed from duree_expiration
    prochain_terme = Column(String(100))
    lib_etat_contrat = Column(String(100))
    branche = Column(String(100))
    somme_quittances = Column(Numeric)  # Changed from somme_guittances
    statut_paiement = Column(String(50))
    capital_assure = Column(Numeric)
    
    # Relationships
    account = relationship("Account", back_populates="contrats")
    garanties = relationship("GarantieContrat", back_populates="contrat")
    sinistres = relationship("Sinistre", back_populates="contrat")


class Sinistre(Base):
    __tablename__ = "sinistres"
    
    num_sinistre = Column(String(50), primary_key=True, autoincrement=False)
    num_contrat = Column(String(50), ForeignKey("contrats.num_contrat"), nullable=False)
    # Note: ref_personne is not in the actual database table
    lib_branche = Column(String(100))
    lib_sous_branche = Column(String(100))
    lib_produit = Column(Text)
    nature_sinistre = Column(String(100))
    lib_type_sinistre = Column(String(100))
    taux_responsabilite = Column(Numeric)
    date_survenance = Column(Date)
    date_declaration = Column(Date)
    date_ouverture = Column(Date)
    observation_sinistre = Column(Text)
    lib_etat_sinistre = Column(String(100))
    lieu_accident = Column(Text)
    motif_reouverture = Column(Text)
    montant_encaisse = Column(Numeric)
    montant_a_encaisser = Column(Numeric)
    
    # Relationships
    contrat = relationship("Contrat", back_populates="sinistres")
