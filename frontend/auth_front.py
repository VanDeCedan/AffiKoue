from dotenv import load_dotenv
import os
import requests
import pandas as pd 

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5000")  # Default to local backend

def login(user_username, user_password):
    response = requests.post(f"{BACKEND_URL}/api/login", json={"user_username": user_username, "user_password": user_password})
    return response

def register(user_username, user_nom_prenoms, user_departement, user_email, user_password, user_roles):
    response = requests.post(f"{BACKEND_URL}/api/register", json={"user_username": user_username, "user_nom_prenoms": user_nom_prenoms, "user_departement": user_departement, "user_email": user_email, "user_password": user_password, "user_roles": user_roles})
    return response.json()

def get_user_roles(token):
    response = requests.get(f"{BACKEND_URL}/api/protected", headers={"Authorization": f"Bearer {token}"})
    response.raise_for_status()  # Raise an error for bad responses
    data = response.json()
    if "user" in data and "user_roles" in data["user"]:
        return data["user"]["user_roles"]
    return None

def get_user_nom(token):
    response=requests.get(f"{BACKEND_URL}/api/protected", headers={"Authorization": f"Bearer {token}"})
    response.raise_for_status()  # Raise an error for bad responses
    data = response.json()
    if "user" in data and "user_nom_prenoms" in data["user"]:
        return data["user"]["user_nom_prenoms"]
    return None

def is_first_user():
    response = requests.get(f"{BACKEND_URL}/api/is_first_user")
    return response.json().get('is_first', False)

def get_users_list():
    response = requests.get(f"{BACKEND_URL}/api/list_of_values", params={"table_name": "users", "column_name": "user_username"})
    data = response.json()
    return data.get('values', [])

def update_user_info(user_username, info_type, info_value):
    response = requests.post(
        f"{BACKEND_URL}/api/update_user_info",
        json={
            "user_username": user_username,
            "info_type": info_type,
            "info_value": info_value
        }
    )
    return response.json()

def delete_user(user_username):  
    response = requests.post(f"{BACKEND_URL}/api/delete_user", json={"user_username": user_username})
    return response.json()

def get_users_df(Username):
    response = requests.get(f"{BACKEND_URL}/api/get_users_table_as_df")
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        if Username :
            df = df[df["Username"] == Username]
        return df
    else:
        result = f"Error: {response.status_code} - {response.text}"
        return result