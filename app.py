import pandas as pd
import numpy as np
import sqlite3 as sql
import streamlit as st
from datetime import datetime
import plotly.express as px
import streamlit as st
from authentication import authenticate
from user_management import create_user, get_user_names, get_user_department, delete_user, get_all_users

# backend
def conn():
    con = sql.connect("data/finance.db")
    c = con.cursor()
    return con, c

def creer_tables():
    con, c = conn()
    c.executescript("""
CREATE TABLE IF NOT EXISTS budget (b_code_activite INTEGER PRIMARY KEY, 
b_projet TEXT,b_code_resultat TEXT,b_item_code TEXT,b_montant INTEGER, b_depense INTEGER,
solde INTEGER,b_departement TEXT)
;
CREATE TABLE IF NOT EXISTS users (nom_prenom TEXT PRIMARY KEY, u_departement TEXT)
;
CREATE TABLE IF NOT EXISTS requete (id TEXT PRIMARY KEY,id_requete TEXT,type_activite TEXT,
nom TEXT,code_requete INTEGER,type_requete TEXT,demandeur TEXT,r_code_activite INTEGER,
r_montant INTEGER,date DATETIME DEFAULT CURRENT_TIMESTAMP,r_projet TEXT,r_code_resultat TEXT,r_item_code TEXT,r_departement TEXT)
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
    con, _ = conn()
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

def recuperer_valeurs_colonne(table_name,search_col,search_val,cols:list):
    con, c = conn()
    col_str = ", ".join(cols)
    query = f"""SELECT {col_str} FROM {table_name} WHERE {search_col} = ?"""
    c.execute(query, (search_val,))
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

def depense_par_code_activite():
    con, _= conn()
    df_budget=pd.read_sql(""" SELECT * FROM budget """,con)
    df_requete=pd.read_sql(""" SELECT * FROM requete """,con)
    df_reconciliation=df_requete[df_requete["type_activite"]=="Reconciliation"]
    df_requete_emis=df_requete[df_requete["type_activite"]!="Reconciliation"]
    df_req_non_reconcilie=df_requete_emis[~df_requete_emis["code_requete"].isin(df_reconciliation["code_requete"])]
    df_depenses=pd.concat([df_req_non_reconcilie,df_reconciliation],axis=0)
    df_budget["b_depense"]=df_budget["b_code_activite"].map(df_depenses.groupby("r_code_activite")["r_montant"].sum())
    df_budget["b_depense"]=df_budget["b_depense"].fillna(0).astype(int)
    df_budget.to_sql("budget", con,if_exists="replace", index=False)
    con.close()

def calcul_solde():
    con, c= conn()
    query= """ UPDATE budget SET solde = b_montant - b_depense"""
    c.execute(query)
    con.commit()
    con.close()

def col_budget_to_df(columns_old_names, new_names):
    con, _= conn()
    df = pd.read_sql("SELECT * FROM budget", con) #Recuperation des données de la table budget
    if len(columns_old_names) != len(new_names):
        raise ValueError("Le nombre de colonnes sélectionnées doit correspondre au nombre de nouveaux noms.")
    df_budget = df[columns_old_names].copy() # Sélectionner les colonnes et les renommer
    df_budget.columns = new_names
    con.close()
    return df_budget

def somaire_budget():
    con, _= conn()
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
    # Authentification
    name, username, roles = authenticate()
    
    if name:
        st.sidebar.title(f"Bienvenu {name}")
        # Afficher les options du menu en fonction des rôles
        if "users" in roles:
            st.sidebar.write("🛠 **Options Admin**")
            user_option=st.sidebar.selectbox("Utilisateur",["Créer un utilisateur", "Supprimer un utilisateur","Liste des utilisateurs"],index=None)
            if user_option=="Créer un utilisateur":
                with st.form("create_user_form"):
                    nom_prenoms = st.text_input("Nom & Prénoms")
                    u_department = st.selectbox("Département", ["DFA", "DRHA", "DMMC", "DSR/SMNI", "DRSE", "DAI", "DARS3", "DHASE"], index=None)
                    username = st.text_input("Nom d'utilisateur")
                    password = st.text_input("Mot de passe", type="password")
                    roles = st.multiselect("Roles", ["users", "budget", "requete", "reconciliation", "dashboard"])
                    submit = st.form_submit_button("Créer")
                    if submit:
                        result = create_user(nom_prenoms, u_department, username, password, roles)
                        st.success(result)
            elif user_option=="Supprimer un utilisateur":
                user_to_delete = st.selectbox("Utilisateur à supprimer", get_user_names(), index=None)
                if user_to_delete:
                    result = delete_user(user_to_delete)
                    st.success(result)
            elif user_option=="Liste des utilisateurs":
                users_df=get_all_users()
                if not users_df.empty:
                    st.dataframe(users_df)    

        # Créer les options du MENU
        if "budget" in roles:
            budget_option=st.sidebar.selectbox("Budget", ["Ajouter budget","Voir Budget"],index=None)
        if "requete" in roles:
            requete_option=st.sidebar.selectbox("Requete", ["Requête initiale", "Requête complémentaire", "Requête à annuler"],index=None)
        if "reconciliation" in roles:
            reconciliation_option=st.sidebar.selectbox("Reconciliation", ["Saisir reconciliation"],index=None)
        if "dashboard" in roles:
            dashboard_option=st.sidebar.selectbox("Dashboard", ["Afficher solde","Point budgétaire", "Consommation"],index=None)
    
    # Afficher les options du menu       
        if budget_option=="Ajouter budget":
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
                demandeur=st.selectbox("Demandeur", get_user_names(),index=None)
                r_code_activite=st.selectbox("Code Activité", valeurs_uniques("budget", "b_code_activite"),index=None)
                r_montant=st.number_input("Montant de l'activité : ", step=1, value=None)
                if st.form_submit_button("Enregistrer"):
                    # Verfirier si tout les champs sont remplis
                    if nom and type_requete and demandeur and r_code_activite and r_montant:
                        last_req_code = get_last_req_code()
                        code_requete = last_req_code + 1
                        id=code_requete
                        id_requete=code_requete
                        r_projet, r_code_resultat, r_item_code = recuperer_valeurs_colonne("budget", "b_code_activite",r_code_activite, ["b_projet", "b_code_resultat", "b_item_code"])
                        r_departement=get_user_department(demandeur)
                        values_to_sqlcols("requete", ["id", "id_requete" ,"type_activite", "nom", "code_requete", "type_requete", "demandeur", "r_code_activite", "r_montant", "r_projet", "r_code_resultat", "r_item_code", "r_departement"], [id,id_requete,requete_option, nom, code_requete, type_requete, demandeur, r_code_activite, r_montant, r_projet, r_code_resultat, r_item_code, r_departement])
                        depense_par_code_activite()
                        calcul_solde()
                        df=col_budget_to_df(["b_code_activite","solde"],["b_code_activite","Solde"])
                        solde=df.loc[df["b_code_activite"]==r_code_activite, "Solde"].values[0]
                        solde=int(solde)
                        st.success(f"Requête ajoutée avec succès \n")
                        st.success(f"Code de la requête : {code_requete} \n")
                        st.success(f"Solde restant sur la ligne : {solde:,}")
                    else:
                        st.error("Veuillez remplir tous les champs.")
        elif requete_option=="Requête complémentaire":
            with st.form("requete_form"):
                code_requete=st.selectbox("Code Requête", valeurs_uniques("requete", "code_requete"),index=None)
                nom=st.text_input("Nom de la requête")
                type_requete=st.selectbox("Type de requête", ["Avance de voyage", "Achat de biens ou de service"],index=None)
                demandeur=st.selectbox("Demandeur", get_user_names(),index=None)
                r_code_activite=st.selectbox("Code Activité", valeurs_uniques("budget", "b_code_activite"),index=None)
                r_montant=st.number_input("Montant de l'activité : ", step=1, value=None)
                if st.form_submit_button("Enregistrer"):
                    # Verfirier si tout les champs sont remplis
                    if code_requete and nom and type_requete and demandeur and r_code_activite and r_montant:
                        last_sub_activity= count_sub_activities(code_requete)
                        id=str(code_requete) + "_" + str(last_sub_activity+1)
                        id_requete=id
                        r_projet, r_code_resultat, r_item_code = recuperer_valeurs_colonne("budget", "b_code_activite", r_code_activite,["b_projet", "b_code_resultat", "b_item_code"])
                        r_departement=get_user_department(demandeur)
                        values_to_sqlcols("requete", ["id","id_requete","type_activite", "nom", "code_requete", "type_requete", "demandeur", "r_code_activite", "r_montant", "r_projet", "r_code_resultat", "r_item_code", "r_departement"], [id,id_requete,requete_option, nom, code_requete, type_requete, demandeur, r_code_activite, r_montant, r_projet, r_code_resultat, r_item_code, r_departement])
                        depense_par_code_activite()
                        calcul_solde()
                        df=col_budget_to_df(["b_code_activite","solde"],["b_code_activite","Solde"])
                        solde=df.loc[df["b_code_activite"]==r_code_activite, "Solde"].values[0]
                        solde=int(solde)
                        st.success(f"Requête ajoutée avec succès. \n")
                        st.success(f"Code de la requête complémentaire : {id}. \n")
                        st.success(f"Code de la requête : {code_requete}. \n")
                        st.success(f"Solde restant sur la ligne : {solde:,}. \n")
        elif requete_option=="Requête à annuler":
            with st.form("requete_form"):
                id_requete=st.selectbox("Code Requête", valeurs_uniques("requete", "id_requete"),index=None)
                if st.form_submit_button("Enregistrer"):
                    if id_requete :
                        id=id_requete + "_" + "annule"
                        r_departement,r_projet, r_code_resultat, r_item_code,code_requete,nom,type_requete,demandeur,r_code_activite,r_montant=recuperer_valeurs_colonne("requete", "id_requete",id_requete, ["r_departement","r_projet", "r_code_resultat", "r_item_code","code_requete","nom","type_requete","demandeur","r_code_activite","r_montant"])
                        r_montant=-r_montant
                        values_to_sqlcols("requete", ["id", "id_requete","type_activite", "nom", "code_requete", "type_requete", "demandeur", "r_code_activite", "r_montant", "r_projet", "r_code_resultat", "r_item_code", "r_departement"], [id, id_requete,requete_option, nom, code_requete, type_requete, demandeur, r_code_activite, r_montant,r_projet , r_code_resultat, r_item_code, r_departement])
                        depense_par_code_activite()
                        calcul_solde()
                        df=col_budget_to_df(["b_code_activite","solde"],["b_code_activite","Solde"])
                        solde=df.loc[df["b_code_activite"]==r_code_activite, "Solde"].values[0]
                        solde=int(solde)
                        st.success(f"Requête {id_requete} annullée avec succès. \n")
                        st.success(f"Solde restant sur la ligne : {solde:,}. \n")
        elif reconciliation_option=="Saisir reconciliation":
            with st.form("reconciliation_form"):
                code_requete=st.selectbox("Code Requête", valeurs_uniques("requete", "code_requete"),index=None)
                r_montant=st.number_input("Montant de la reconciliation : ", step=1, value=None)
                if st.form_submit_button("Enregistrer"):
                    if code_requete:
                        id=str(code_requete) + "_" + "reconcilie"
                        id_requete=str(code_requete)
                        r_departement,r_projet, r_code_resultat, r_item_code,nom,type_requete,demandeur,r_code_activite=recuperer_valeurs_colonne("requete", "id_requete", id_requete,["r_departement","r_projet", "r_code_resultat", "r_item_code","nom","type_requete","demandeur","r_code_activite"])
                        id_requete=id
                        values_to_sqlcols("requete", ["id", "id_requete","type_activite", "nom", "code_requete", "type_requete", "demandeur", "r_code_activite", "r_montant", "r_projet", "r_code_resultat", "r_item_code", "r_departement"], [id, id_requete,requete_option, nom, code_requete, type_requete, demandeur, r_code_activite, r_montant, r_projet, r_code_resultat, r_item_code, r_departement])
                        depense_par_code_activite()
                        calcul_solde()
                        df=col_budget_to_df(["b_code_activite","solde"],["b_code_activite","Solde"])
                        solde=df.loc[df["b_code_activite"]==r_code_activite, "Solde"].values[0]
                        solde=int(solde)
                        st.success(f"Reconciliation de la requête {code_requete} enrégistrée avec succès. \n")
                        st.success(f"Solde restant sur la ligne : {solde:,}. \n")
        elif dashboard_option=="Afficher solde":
            col1, col2 = st.columns(2)
            with col1:
                st.write("Solde par Code Activité")
                r_code_activite=st.selectbox("Code Activité", valeurs_uniques("budget", "b_code_activite"),index=None)
                if r_code_activite:
                    df=col_budget_to_df(["b_code_activite","solde"],["Code activité","Solde"])
                    df_solde=df[df["Code activité"]==r_code_activite]
                    df_solde["Code activité"]=df_solde["Code activité"].astype(str)
                    df_solde["Solde"]=df_solde["Solde"].astype(int)
                    st.dataframe(df_solde,width=250,hide_index=True)
            with col2:
                st.write("Solde par Projet")
                r_projet=st.selectbox("Projet", valeurs_uniques("budget", "b_projet"),index=None)
                if r_projet:
                    df=col_budget_to_df(["b_projet","solde"],["Projet","Solde"])
                    df_solde=df[df["Projet"]==r_projet]
                    df_solde["Solde"]=df_solde["Solde"].astype(int)
                    df_solde_grouped=df_solde.groupby("Projet")["Solde"].sum().reset_index()
                    st.dataframe(df_solde_grouped,width=250,hide_index=True)
        elif dashboard_option=="Point budgétaire":
            st.title("Point des requêtes")
            col1,col2=st.columns(2)
            with col1:
                st.write("Requêtes initiées")
                with st.container():
                    demandeur=st.selectbox("Initiateur",valeurs_uniques("requete","demandeur"),index=None)
                    con=sql.connect("data/finance.db")
                    if demandeur:
                        df=pd.read_sql(f""" SELECT * FROM requete WHERE demandeur='{demandeur}' """,con)
                        con.close()
                        df_requete=df[df["type_activite"]!="Reconciliation"]
                        df_requete["n_date"]=df_requete["date"].str.split().str[0] # Enlever l'heure de la date
                        df_requete=df_requete[["type_activite","nom","r_montant","n_date"]]
                        df_requete.rename(columns={"type_activite":"Type d'activité","nom":"Nom","r_montant":"Montant","n_date":"Date"},inplace=True)
                        st.dataframe(df_requete,hide_index=True)
                        con.close()
                with st.container():
                    r_departement=st.selectbox("Departement initiateur",valeurs_uniques("requete","r_departement"),index=None)
                    con=sql.connect("data/finance.db")
                    if r_departement:
                        df=pd.read_sql(f""" SELECT * FROM requete WHERE r_departement='{r_departement}' """,con)
                        con.close()
                        df_requete=df[df["type_activite"]!="Reconciliation"]
                        df_requete["n_date"]=df_requete["date"].str.split().str[0] # Enlever l'heure de la date
                        df_requete=df_requete[["type_activite","nom","r_montant","n_date"]]
                        df_requete.rename(columns={"type_activite":"Type d'activité","nom":"Nom","r_montant":"Montant","n_date":"Date"},inplace=True)
                        st.dataframe(df_requete,hide_index=True)
            with col2:
                st.write("Requêtes non reconciliées")
                with st.container():
                    demandeur=st.selectbox("Responsable",valeurs_uniques("requete","demandeur"),index=None)
                    con=sql.connect("data/finance.db")
                    if demandeur:
                        df=pd.read_sql(f""" SELECT * FROM requete WHERE demandeur='{demandeur}' """,con)
                        con.close()
                        df_reconciliation=df[df["type_activite"]=="Reconciliation"]
                        df_requete=df[df["type_activite"]=="Requête initiale"]
                        df_non_reconci=df_requete[~df_requete["code_requete"].isin(df_reconciliation["code_requete"])]
                        df_non_reconci["n_date"]=df_non_reconci["date"].str.split().str[0] # Enlever l'heure de la date
                        df_non_reconci=df_non_reconci[["type_activite","nom","r_montant","n_date"]]
                        df_non_reconci.rename(columns={"type_activite":"Type d'activité","nom":"Nom","r_montant":"Montant","n_date":"Date"},inplace=True)
                        st.dataframe(df_non_reconci,hide_index=True)   
                with st.container():
                    r_departement=st.selectbox("Departement  responsable",valeurs_uniques("requete","r_departement"),index=None)
                    con=sql.connect("data/finance.db")
                    if r_departement:
                        df=pd.read_sql(f""" SELECT * FROM requete WHERE r_departement='{r_departement}' """,con)
                        con.close()
                        df_reconciliation=df[df["type_activite"]=="Reconciliation"]
                        df_requete=df[df["type_activite"]=="Requête initiale"]
                        df_non_reconci=df_requete[~df_requete["code_requete"].isin(df_reconciliation["code_requete"])]
                        df_non_reconci["n_date"]=df_non_reconci["date"].str.split().str[0] # Enlever l'heure de la date
                        df_non_reconci=df_non_reconci[["type_activite","nom","r_montant","n_date"]]
                        df_non_reconci.rename(columns={"type_activite":"Type d'activité","nom":"Nom","r_montant":"Montant","n_date":"Date"},inplace=True)
                        st.dataframe(df_non_reconci,hide_index=True)   
        elif dashboard_option == "Consommation":
            st.write("Consommation par Projets")
            df = col_budget_to_df(["b_projet", "b_depense", "b_montant"], ["Code projet", "Depense", "Montant"])
            df_consommation = df.groupby("Code projet")[["Depense", "Montant"]].sum().reset_index()
            df_consommation["Conssomation"] = df_consommation["Depense"] / df_consommation["Montant"]
            # Mettre la consommation en pourcentage
            df_consommation["Conssomation"] = df_consommation["Conssomation"]*100
            df_consommation["Code projet"] = df_consommation["Code projet"].astype(str)
            
            # Create a bar chart with Plotly
            fig = px.bar(df_consommation, x="Code projet", y="Conssomation", text="Conssomation")

            # Update the layout to show labels on bars
            fig.update_traces(texttemplate="%{text:.1f}", textposition="inside", textfont_size=18)

            # Display the chart in Streamlit
            st.plotly_chart(fig)
        
if __name__ == "__main__":
    main()