import sqlite3
import pandas as pd
import streamlit as st
import numpy as np
import openpyxl as px
from io import BytesIO

# Connexion à la base de données
conn = sqlite3.connect("data/budget.db")
c= conn.cursor()
# Création des tables
c.executescript("""
CREATE TABLE IF NOT EXISTS budget (
    code_activite PRIMARY KEY,
    projet,
    code_resultat,
    item_code,
    montant,
    departement
);
                                     
CREATE TABLE IF NOT EXISTS activite (
    code_genere INTEGER PRIMARY KEY AUTOINCREMENT,
    nom,
    type,
    montant,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    projet,
    code_resultat,
    code_activite,
    item_code,
    demandeur,
    departement,
    FOREIGN KEY (code_activite) REFERENCES Budget(code_activite)
);
                     
CREATE TABLE IF NOT EXISTS solde (
    code_activite PRIMARY KEY,
    projet,
    code_resultat,
    item_code,
    montant,
    departement,
    FOREIGN KEY (code_activite) REFERENCES Budget(code_activite) 
);               

CREATE TABLE IF NOT EXISTS annulation (
    code_genere INTEGER PRIMARY KEY AUTOINCREMENT,
    nom,
    type,
    montant,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    projet,
    code_resultat,
    code_activite,
    item_code,
    demandeur,
    departement,
    FOREIGN KEY (code_activite) REFERENCES Budget(code_activite)
);
""")

# Valider et fermer la connexion
conn.commit()
conn.close()

#Liste des demandeurs 
demandeurs = ["Bob", "Jan", "Paul"]

# Fonction pour enregistrer des utilisateurs avec un nom d'utilisateur, un logging et un mot de passe hasher


# Fonction pour insérer le budget
def inserer_budget(fichier_xlsx):
    # Connexion à la base de données
    conn = sqlite3.connect("data/budget.db")
    c= conn.cursor()
    # Lecture du fichier Excel
    df = pd.read_excel(fichier_xlsx)
    # Insertion des données dans la table Budget
    df.to_sql("budget", conn, if_exists="append", index=False)
    st.success(f"Nombre d'activité ajoutées {str(df.shape[0])}")
    # Valider et fermer la connexion
    conn.commit()
    conn.close()

# Function to fetch unique values from the database
def valeurs_uniques(db_path, table_name, column_name):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    c= conn.cursor()
    # Query to fetch unique values from the specified column
    query = f"SELECT DISTINCT {column_name} FROM {table_name}"
    c.execute(query)
    # Fetch all unique values
    val_uniques = [row[0] for row in c.fetchall()]
    # Close the connection
    conn.close()
    return val_uniques

def saisie_activite():
    # Connexion à la base de données
    conn = sqlite3.connect("data/budget.db")
    c = conn.cursor()
    # Saisie des données
    with st.form("form_activite"):
        nom = st.text_input("Nom de l'activité : ")
        type= st.selectbox("Type d'activité : ", ["Requete de voyage", "Achat de biens ou services"])
        montant = st.number_input("Montant de l'activité : ")
        demandeur=st.selectbox("Demandeur : ", demandeurs)
        code_activite = st.selectbox("Code activité : ", valeurs_uniques("data/budget.db", "budget", "code_activite"))
        if code_activite:
            # Query pour récupérer le projet, le code résultat et l'item code pour l'activité donnée
            query = '''
            SELECT projet, code_resultat, item_code
            FROM budget
            WHERE code_activite = ?
            '''
            c.execute(query, (code_activite,))
            # Récupération du projet, code résultats et item code de la table budget
            projet, code_resultat, item_code = c.fetchone()            
        submitted = st.form_submit_button("Ajouter")
        if submitted:
            # Insertion des données dans la table activite
            c.execute("INSERT INTO activite (nom, type, montant, projet, code_resultat, code_activite, item_code) VALUES (?, ?, ?, ?, ?, ?, ?)", (nom, type, montant, projet, code_resultat, code_activite, item_code))
            # Valider et fermer la connexion
            conn.commit()
            conn.close()
            st.success("L'activité a été ajoutée avec succès.")

def saisie_annulation():
    # Connexion à la base de données
    conn = sqlite3.connect("data/budget.db")
    c = conn.cursor()
    # Saisie des données
    with st.form("form_activite"):
        nom = st.selectbox("Nom de l'activité : ", valeurs_uniques("data/budget.db", "activite", "nom"))
        if nom:
            # Query pour récupérer le type, montant, projet, code résultat code activité et item code pour l'activité donnée
            query = '''
            SELECT type, montant, projet, code_resultat, code_activite, item_code
            FROM budget
            WHERE nom = ?
            '''
            c.execute(query, (nom,))
            # Récupération du projet, code résultats et item code de la table budget
            type, montant, projet, code_resultat, code_activite, item_code = c.fetchone()  
        submitted = st.form_submit_button("Ajouter")
        if submitted:
            # Insertion des données dans la table activite
            c.execute("INSERT INTO activite (nom, type, montant, projet, code_resultat, code_activite, item_code) VALUES (?, ?, ?, ?, ?, ?, ?)", (nom, type, montant, projet, code_resultat, code_activite, item_code))
            # Valider et fermer la connexion
            conn.commit()
            conn.close()
            st.success("L'activité a été annulée avec succès.")

def calculer_solde_activite():
    # Connexion à la base de données
    conn = sqlite3.connect("data/budget.db")
    c = conn.cursor()
    #Recuperation des données des tables budget et activite dans un dataframe 
    df_budget = pd.read_sql("SELECT * FROM budget", conn)
    df_activite = pd.read_sql("SELECT * FROM activite", conn)
    #Calculer le montant total par code_activite
    montant_total = df_activite.groupby("code_activite")["montant"].sum()
    #Calculer le solde
    df_budget["solde"] = df_budget["montant"] - df_budget["code_activite"].map(montant_total)
    #Supprimer montant
    df_budget.drop("montant", axis=1, inplace=True)
    #Insertion des données dans la table solde
    df_budget.to_sql("solde", conn, if_exists="replace", index=False)     
    # Valider et fermer la connexion
    conn.commit()
    conn.close()

def calculer_solde_annulation():
    # Connexion à la base de données
    conn = sqlite3.connect("data/budget.db")
    c = conn.cursor()
    #Recuperation des données des tables budget et annulation dans un dataframe 
    df_budget = pd.read_sql("SELECT * FROM budget", conn)
    df_annulation = pd.read_sql("SELECT * FROM annulation", conn)
    #Calculer le montant total par code_activite
    montant_total = df_annulation.groupby("code_activite")["montant"].sum()
    #Calculer le solde
    df_budget["solde"] = df_budget["montant"] + df_budget["code_activite"].map(montant_total)
    #Supprimer montant
    df_budget.drop("montant", axis=1, inplace=True)
    #Insertion des données dans la table solde
    df_budget.to_sql("solde", conn, if_exists="replace", index=False)     
    # Valider et fermer la connexion
    conn.commit()
    conn.close()

def afficher_solde():
    # Connexion à la base de données
    conn = sqlite3.connect("data/budget.db")
    c = conn.cursor()
    #Recuperation des données de la table solde
    df_solde = pd.read_sql("SELECT * FROM solde", conn)
    # Fitrer le solde par code_activite
    code_activite = st.selectbox("Code activité : ", valeurs_uniques("data/budget.db", "solde", "code_activite"))
    df_solde = df_solde[df_solde["code_activite"] == code_activite]
    #Affichage des données
    st.dataframe(df_solde)
    # Valider et fermer la connexion
    conn.commit()
    conn.close()

# Application streamlit 
st.markdown("<h1 style='text-align: center; color: green;'>AffiKoue</h1>", unsafe_allow_html=True)

# Menu
st.sidebar.title("Menu")   
budget_option=st.sidebar.selectbox("Budget", ["Ajouter budget", "Ajouter activité", "Annulation d'activité", "Afficher solde"])

if budget_option == "Ajouter budget":
    fichier_xlsx = st.file_uploader("Télécharger le fichier Excel", type=["xlsx"])
    if fichier_xlsx:
        inserer_budget(fichier_xlsx)

elif budget_option == "Ajouter activité":
    saisie_activite()
    
elif budget_option == "Annulation d'activité":
    saisie_annulation()

elif budget_option == "Afficher solde":
    calculer_solde_activite()
    calculer_solde_annulation()
    afficher_solde()
