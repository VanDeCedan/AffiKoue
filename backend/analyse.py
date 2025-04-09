import pandas as pd
from backend.db import db_connect, psycopg2_connect
import backend.dp as dp
import backend.budget as budget

def get_df_budget(projet):
    df_f = dp.get_table_as_df("budget",["budget_code_activite","budget_solde","budget_consommation","budget_projet"],
                            ["Code activité","Solde","Consommation","Projet"])
    df_f = df_f.loc[df_f["Projet"] == projet]
    df_f["Consommation"] = df_f["Consommation"] * 100
    return df_f

def get_df_requete_non_reconcile():
    df_requete=dp.get_table_as_df("requete",["requete_nom_activite","requete_code_requete_init","requete_montant"],
                            ["Nom activité","Code requête","Montant"])
    df_reconciliation=dp.get_table_as_df("reconciliation",["reconciliation_code_requete"],["Code requête"])
    df_requete_non_reconcilie = df_requete[~df_requete["Code requête"].isin(df_reconciliation["Code requête"])]
    # dataframe des requêtes non réconciliées groupées par code requête
    df_f=df_requete_non_reconcilie.groupby("Code requête").agg({"Montant": "sum"}).reset_index()
    return df_f

def get_consomation_par_projet():
    df_f = dp.get_table_as_df("budget",["budget_code_activite","budget_projet","budget_consommation"],
                            ["Code activité","Projet","Consommation"])
    df_f["Consommation"] = df_f["Consommation"] * 100
    # groupé la moyenne de consommation par projet
    df_f_grouped = df_f.groupby("Projet")["Consommation"].mean().reset_index()
    return df_f_grouped
