from dotenv import load_dotenv
import os
import requests
import pandas as pd 

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5000")  # Default to local backend

#*****************************************Insertion*********************************************************
def insert_budget_file(xlsx_path):
    """Send the Excel file to Flask API to insert into PostgreSQL."""
    with open(xlsx_path, "rb") as file:
        response = requests.post(
            f"{BACKEND_URL}/api/insert_budget",
            files={"file": file}
        )
    return response.json()

#**********************************Voir Budget************************************
def get_projet_list():
    response = requests.get(f"{BACKEND_URL}/api/list_of_values", params={"table_name": "budget", "column_name": "budget_projet"})
    data = response.json()
    return data.get('values', [])

def get_budget_df(Projet):
    response = requests.get(f"{BACKEND_URL}/api/budget_as_df")
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        if Projet :
            df = df[df["Projet"] == Projet]
        return df
    else:
        result = f"Error: {response.status_code} - {response.text}"
        return result

#**************************************Solde************************************************************************************
def get_depense_par_activite(code_activite):
    url = f"{BACKEND_URL}/api/calcul_depense_code_activite"
    try:
        response = requests.get(url, params={"budget_code_activite": code_activite})
        if response.status_code == 200:
            return response.json().get("montant_depense", 0.0)
        return 0.0
    except Exception as e:
        return f"Erreur récupération dépense: {e}"

def post_inserer_depense(code_activite):
    url = f"{BACKEND_URL}/api/inserer_depenses"
    try:
        response = requests.post(url, params={"budget_code_activite": code_activite})
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_solde_par_activite(code_activite):
    url = f"{BACKEND_URL}/api/calcul_solde_code_actvite"
    try:
        response = requests.get(url, params={"budget_code_activite": code_activite})
        if response.status_code == 200:
            return response.json().get("solde", 0.0)
        return 0.0
    except Exception as e:
        return f"Erreur récupération solde: {e}"

def post_inserer_solde(code_activite):
    url = f"{BACKEND_URL}/api/inserer_solde"
    try:
        response = requests.post(url, params={"budget_code_activite": code_activite})
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_consommation_par_activite(code_activite):
    url = f"{BACKEND_URL}/api/calcul_consommation_code_activite"
    try:
        response = requests.get(url, params={"budget_code_activite": code_activite})
        if response.status_code == 200:
            return response.json().get("consommation", 0.0)
        return 0.0
    except Exception as e:
        return f"Erreur récupération consommation: {e}"


def post_inserer_consommation(code_activite):
    url = f"{BACKEND_URL}/api/inserer_consommation"
    try:
        response = requests.post(url, params={"budget_code_activite": code_activite})
        return response.json()
    except Exception as e:
        return {"error": str(e)}