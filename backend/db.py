import psycopg2
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

db=SQLAlchemy()

class User(db.Model):
    __tablename__="users"
    user_username       = db.Column(db.String(80), primary_key=True)
    user_nom_prenoms    = db.Column(db.String(80), nullable=False)
    user_departement    = db.Column(db.String(80), nullable=False)
    user_email          = db.Column(db.String(120), unique=True, nullable=False)
    user_password       = db.Column(db.String(500), nullable=False)
    user_roles          = db.Column(db.String(80), nullable=False)

class Budget(db.Model):
    __tablename__="budget"
    budget_code_activite    = db.Column(db.Integer, primary_key=True)
    budget_code_projet      = db.Column(db.String(80), nullable=False)
    budget_code_resultat    = db.Column(db.String(80))
    budget_item_code        = db.Column(db.String(80), nullable=False)
    budget_montant_initial  = db.Column(db.Integer, nullable=False)
    budget_montant_depense  = db.Column(db.Integer)
    budget_solde            = db.Column(db.Integer)
    budget_consommation     = db.Column(db.Integer)
    budget_projet           = db.Column(db.String(80), nullable=False)

class Requete(db.Model):
    __tablename__="requete"
    requete_id                    = db.Column(db.String(80), primary_key=True)
    requete_type_requete          = db.Column(db.String(80), nullable=False)
    requete_code_requete_init     = db.Column(db.String(80), nullable=False)
    requete_code_requete_cplmt    = db.Column(db.String(80))
    requete_nom_activite          = db.Column(db.String(500), nullable=False)
    requete_type_objet            = db.Column(db.String(80), nullable=False)
    requete_demandeur             = db.Column(db.String(80), nullable=False)
    requete_code_activite         = db.Column(db.Integer, nullable=False)
    requete_montant_avance_voyage = db.Column(db.Integer, nullable=False)
    requete_montant_achat         = db.Column(db.Integer, nullable=False)
    requete_montant_momo          = db.Column(db.Integer, nullable=False)
    requete_montant               = db.Column(db.Integer, nullable=False)
    requete_date                  = db.Column(db.DateTime, nullable=False)
    requete_status                = db.Column(db.String(80), nullable=False)

class Reconciliation(db.Model):
    __tablename__="reconciliation"
    reconciliation_id               = db.Column(db.String(80), primary_key=True)
    reconciliation_code_requete     = db.Column(db.String(80), nullable=False)
    reconciliation_nom_activite        = db.Column(db.String(300), nullable=False)
    reconciliation_code_activite    = db.Column(db.Integer, nullable=False)
    reconciliation_code_projet      = db.Column(db.String(80), nullable=False)
    reconciliation_code_resultat    = db.Column(db.String(80), nullable=False)
    reconciliation_item_code        = db.Column(db.String(80), nullable=False)
    reconciliation_montant          = db.Column(db.Integer, nullable=False)

def db_connect():
    db_url = os.getenv("url")  # Ensure your environment variable contains the full database URL
    if not db_url:
        raise ValueError("Database URL not found in environment variables.")
    engine = create_engine(db_url)  # Create a SQLAlchemy engine
    return engine

def psycopg2_connect():
    conn = psycopg2.connect(os.getenv("url"))
    return conn