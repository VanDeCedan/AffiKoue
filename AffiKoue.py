import pandas as pd
import numpy as np
import sqlite3 as sql
import streamlit as st
from datetime import datetime

# backend
def conn():
    con = sql.connect("data/finance.db")
    c = con.cursor()
    return con, c

def creer_tables():
    con, c = conn()
    c.executescript("""
CREATE TABLE IF NOT EXISTS budget (b_code_activite INTEGER PRIMARY KEY, 
b_projet,b_code_resultat,b_item_code,b_montant INTEGER, b_depense INTEGER,
solde INTEGER,b_departement)
;
CREATE TABLE IF NOT EXISTS users (nom_prenom TEXT PRIMARY KEY, u_departement)
;
CREATE TABLE IF NOT EXISTS requete (id PRIMARY KEY,type_activite,
nom,code_requete INTEGER,type_requete,demandeur,r_code_activite INTEGER,
r_montant INTEGER, reconciliation INTEGER, r_depense INTEGER,
date DATETIME DEFAULT CURRENT_TIMESTAMP,r_projet,r_code_resultat,r_item_code,r_departement)
""")
    con.commit()  # enregistrer
    con.close()  # fermer la connection

def verifier_utilisateurs_existant(nom_prenom):
    con, c = conn()
    c.execute("SELECT * FROM users")
    df=pd.read_sql("SELECT * FROM users", con)
    find=df["nom_prenom"].str.contains(nom_prenom).any()
    return find

def inserer_utilisateurs(nom_prenom, u_departement):
    con, c = conn()
    c.execute("INSERT INTO users (nom_prenom, u_departement) VALUES (?,?)", (nom_prenom, u_departement))
    con.commit()
    con.close()

def recuperer_departement(nom_prenom):
    con, c = conn()
    c.execute("SELECT u_departement FROM users WHERE nom_prenom=?", (nom_prenom,))
    departement = c.fetchone()[0]
    con.close()
    return departement

def inserer_budget(fichier_xlsx):
    con, c = conn()
    df = pd.read_excel(fichier_xlsx) # Lecture du fichier Excel
    df.columns = df.columns.str.replace(" ","").str.strip()
    df.to_sql(f"budget", con, if_exists="append", index=False) # Insertion des données dans la table Budget
    con.commit()
    con.close()
    return df

def valeurs_uniques(table_name, column_name):
    con, c = conn() 
    c.execute(f"SELECT DISTINCT {column_name} FROM {table_name}") # Query to fetch unique values from the specified column
    val_uniques = [row[0] for row in c.fetchall()] # Fetch all unique values
    con.close() # Close the connection
    return val_uniques

# Receuillir le code de la dernière requête
def get_last_req_code():
    con, c = conn() 
    c.execute(""" SELECT MAX(code_requete) FROM requete WHERE type_activite='Requête initiale' """)
    last_req = c.fetchone()[0]
    con.close()
    return last_req if last_req else 999  # Default before the first milestone (next will be 1000)

# Commpter le nombre de requête complementaire par activite
def count_sub_activities(code_requete):
    con, c = conn() 
    c.execute("SELECT COUNT(*) FROM requete WHERE code_requete=? AND type_activite='Requête complémentaire'", (code_requete,))
    count = c.fetchone()[0]
    con.close()
    return count

def recuperer_valeurs_colonne(table_name,var_key,cols:list):
    con, c = conn()
    col_str = ", ".join(cols)
    query = f"""SELECT {col_str} FROM {table_name} WHERE {var_key} = ?"""
    c.execute(query, (var_key,))
    result = c.fetchone()
    con.close()
    return list(result) if result else None

def values_to_sqlcols(table_name, table_cols:list, values : list):
    con, c = conn()  
    placeholders = ", ".join(["?" for _ in values])
    col_str = ", ".join(table_cols)
    query = f"INSERT INTO {table_name} ({col_str}) VALUES ({placeholders})"
    c.execute(query, values)
    con.commit()
    con.close()

def depense_base_requete(code_requete):
    con, c= conn() 
    df=pd.read_sql(""" SELECT * FROM requete """,con)
    df2=(df.groupby("code_requete")["r_montant"].sum()).to_frame().reset_index()
    depense=(df2.loc[df2["code_requete"]==code_requete, "r_montant"].values)[0].item()
    # mettre à jour la dépense dans la table requete où le type d'activité est 'Requête initiale'
    c.execute("UPDATE requete SET r_depense=? WHERE code_requete=? AND type_activite='Requête initiale'", (depense, code_requete))
    con.commit()
    con.close()

def depense_base_reconciliation():
    con, c= conn()
    df=pd.read_sql(""" SELECT * FROM requete """,con)
    if df['reconciliation']>1:
        df["r_depense"]=df["reconciliation"]
    df.to_sql("requete", con, if_exists='replace', index=False)

def depense_par_code_activite():
    con, c= conn()
    df_budget=pd.read_sql(""" SELECT * FROM budget """,con)
    df_requete=pd.read_sql(""" SELECT * FROM requete """,con)
    df_budget["b_depense"]=df_budget["b_code_activite"].map(df_requete.groupby("r_code_activite")["r_depense"].sum())
    df_budget.to_sql("budget", con,if_exists="replace", index=False)

def calcul_solde():
    con, c= conn()
    query= """ UPDATE budget SET solde = b_montant - b_depense"""
    c.execute(query)
    con.commit()
    con.close()

def col_budget_to_df(columns_old_names, new_names):
    con, c= conn()
    df = pd.read_sql("SELECT * FROM budget", con) #Recuperation des données de la table budget
    if len(columns_old_names) != len(new_names):
        raise ValueError("Le nombre de colonnes sélectionnées doit correspondre au nombre de nouveaux noms.")
    df_budget = df[columns_old_names].copy() # Sélectionner les colonnes et les renommer
    df_budget.columns = new_names
    con.close()
    return df_budget

def somaire_budget():
    con, c= conn()
    df = pd.read_sql("SELECT * FROM budget", con)
    sum=(df.groupby("b_projet")["b_montant"].sum()).reset_index()
    activite=(df.groupby("b_projet")["b_code_activite"].count()).reset_index()
    df1=pd.merge(sum,activite, on="b_projet")
    df1.columns=["Code Projet", "Montant", "Code activite"]
    return df1

# Fonction pour enregistrer des utilisateurs avec un nom d'utilisateur, un logging et un mot de passe hasher
    
# Créer les tables
creer_tables()

# Fonction de l'application principale
def main():
    st.markdown("<h1 style='text-align: center; color: green;'>SUIVI BUDGETAIRE</h1>", unsafe_allow_html=True)

    # Créer les options du MENU
    st.sidebar.title("Menu")
    user_option=st.sidebar.selectbox("Utilisateurs", ["Ajouter utilisateurs", "Liste des utilisateurs"],index=None)   
    budget_option=st.sidebar.selectbox("Budget", ["Ajouter budget","Voir Budget"],index=None)
    requete_option=st.sidebar.selectbox("Requete", ["Requête initiale", "Requête complémentaire", "Requête à annuler","Reconciliation"],index=None)
    dashboard_option=st.sidebar.selectbox("Dashboard", ["Afficher solde","Point budgétaire", "Consommation"],index=None)
    
    # Actions 
    if user_option=="Ajouter utilisateurs":
        with st.form("Utilisateurs"):
            nom_prenom=st.text_input("Nom de l'utilisateur: ")
            u_departement=st.selectbox("Departement : ",["DFA","DRHA","DMMC", "DSR/SMNI", "DRSE", "DAI", "DARS3","DHASE"],index=None)
            if st.form_submit_button("Ajouter"):
                find=verifier_utilisateurs_existant(nom_prenom)
                if find:
                    st.error(f" Utilisateur {nom_prenom} déjà enrégistré")
                else :
                    inserer_utilisateurs(nom_prenom, u_departement)
                    st.success(f" Utilisateur {nom_prenom} a été bien enrégistré")
    elif user_option=="Liste des utilisateurs":
        con,c=conn()
        df=pd.read_sql("SELECT * FROM users", con)
        df.columns=["Utilisateurs", "Departement"]
        filtre=st.selectbox("Utilisateurs",valeurs_uniques("users","nom_prenom"),index=None)
        st.dataframe(df[df["Utilisateurs"]==filtre],hide_index=True)
        
    elif budget_option=="Ajouter budget":
        with st.form("Budget"):
            file=st.file_uploader("Veuillez charger le budget",type=["XLSX"])
            if st.form_submit_button("Soumettre"):
                df=inserer_budget(file)
                if not df.empty:
                    st.success(f"{df.shape[0]} activités ajoutés")
    elif budget_option=="Voir Budget":
        df=somaire_budget()
        st.write(""" Sommaire du budget  """)
        st.dataframe(df)
    
    elif requete_option=="Requête initiale":
        with st.form("requete_form"):
            nom=st.text_input("Nom de la requête")
            type_requete=st.selectbox("Type de requête", ["Avance de voyage", "Achat de biens ou de service"],index=None)
            demandeur=st.selectbox("Demandeur", valeurs_uniques("users","nom_prenom"),index=None)
            r_code_activite=st.selectbox("Code Activité", valeurs_uniques("budget", "b_code_activite"),index=None)
            r_montant=st.number_input("Montant de l'activité : ", step=1, value=None)
            if st.form_submit_button("Soumettre"):
                # Verfirier si tout les champs sont remplis
                if nom and type_requete and demandeur and r_code_activite and r_montant:
                    last_req_code = get_last_req_code()
                    code_requete = last_req_code + 1
                    id=code_requete
                    r_code_projet, r_code_resultat, r_item_code = recuperer_valeurs_colonne("budget", r_code_activite, ["b_projet", "b_code_resultat", "b_item_code"])
                    r_departement=recuperer_departement(demandeur)
                    values_to_sqlcols("requete", ["id", "type_activite", "nom", "code_requete", "type_requete", "demandeur", "r_code_activite", "r_montant", "r_projet", "r_code_resultat", "r_item_code", "r_departement"], [id, "Requête initiale", nom, code_requete, type_requete, demandeur, r_code_activite, r_montant, r_code_projet, r_code_resultat, r_item_code, r_departement])
                    depense_base_requete(code_requete)
                    depense_par_code_activite()
                    calcul_solde()
                    df=col_budget_to_df(["b_code_activite","solde"],["b_code_activite","Solde"])
                    solde=df.loc[df["b_code_activite"]==r_code_activite, "Solde"].values[0]
                    st.success(f"Requête ajoutée avec succès \n code de la requête : {code_requete} \n solde restant sur la ligne : {solde}")
                else:
                    st.error("Veuillez remplir tous les champs.")  

if __name__ == "__main__":
    main()