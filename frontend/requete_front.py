import requests
import os
from dotenv import load_dotenv
import pandas as pd 

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5000")  # Default to local backend

# 1. Get list of code activite
def get_code_activite_list():
    response = requests.get(f"{BACKEND_URL}/api/list_of_values", params={"table_name": "requete", "column_name": "requete_code_activite"})
    data = response.json()
    return data.get('values', [])

# 1. Get list of code activite
def get_requete_code_requete_cplmt_list():
    response = requests.get(f"{BACKEND_URL}/api/list_of_values", params={"table_name": "requete", "column_name": "requete_code_requete_cplmt"})
    data = response.json()
    return data.get('values', [])

def get_code_requete_list():
    response = requests.get(f"{BACKEND_URL}/api/list_of_values", params={"table_name": "requete", "column_name": "requete_code_requete_init"})
    data = response.json()
    return data.get('values', [])

# 2. Get the code of the last request
def get_code_derniere_requete():
    response = requests.get(f"{BACKEND_URL}/api/code_derniere_requete")
    if response.status_code == 200:
        return response.json()
    return {"error": f"Failed to fetch code: {response.status_code}"}

# 3. Get number of complementary requests based on a request code
def get_nb_requete_complementaire(code_requete_init):
    params = {"requete_code_requete_init": code_requete_init}
    response = requests.get(f"{BACKEND_URL}/api/nb_requete_complementaire", params=params)
    if response.status_code == 200:
        return response.json()
    return {"error": f"impossible de recuillir le nombre de requête complémentaire: {response.status_code}"}

def submit_requete(results):
    if results:
        try:
            response = requests.post(f"{BACKEND_URL}/api/insert_requete",json=results)
            if response.status_code == 200 and response.json().get("success"):
                return response.json()
            else:
                return (f"Erreur lors de l'enregistrement ❌: {response.json().get('message')}")
        except Exception as e:
            return (f"Erreur de connexion au serveur : {e}")


def insert_activity(activity_data: dict):
    response = requests.post(f"{BACKEND_URL}/api/insert_activity", json=activity_data)
    if response.status_code == 201:
        return response.json()
    return {"error": response.json().get("error", f"Failed to insert activity : {response.status_code}")}

def get_cols_vals(table_name: str, search_col: str, search_val, cols: list):
    params = {
        "table_name": table_name,
        "search_col": search_col,
        "search_val": search_val
    }
    # Add list of columns
    for col in cols:
        params["cols"] = params.get("cols", []) + [col]

    response = requests.get(f"{BACKEND_URL}/api/get_vals", params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.json().get("error", "Unknown error")}