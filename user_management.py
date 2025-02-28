from authentication import load_config, save_config
import streamlit_authenticator as stauth
import pandas as pd

def create_user(name, department, username, password, roles):
    """Ajoute un nouvel utilisateur"""
    config = load_config()
    if username in config["users"]:
        return "Nom d'utilisateur déjà existant"

    hashed_password = stauth.Hasher([password]).generate()[0]
    config["users"][username] = {
        "name": name, "department": department,
        "username": username, "password": hashed_password,
        "roles": roles, "created": True
    }
    save_config(config)
    return "Utilisateur créé avec succès"

def get_user_names():
    """Retourne la liste des noms & prénoms des utilisateurs"""
    config = load_config()
    return [user["name"] for user in config["users"].values() if user["created"]]

def get_user_department(name):
    """Retourne le département d'un utilisateur en fonction de son nom"""
    config = load_config()
    for user in config["users"].values():
        if user["name"] == name and user["created"]:
            return user["department"]
    return None

def delete_user(username):
    """Supprime un utilisateur du fichier de configuration"""
    config = load_config()
    if username in config["users"]:
        del config["users"][username]
        save_config(config)
        return f"L'utilisateur {username} a été supprimé avec succès."
    return "Utilisateur introuvable."

def get_all_users():
    """Retourne un DataFrame contenant tous les utilisateurs"""
    config = load_config()
    users_data = [
        {"Nom & Prenoms": user["name"], "Departement": user["department"], "Nom d'utilisateur": username, "Roles": ", ".join(user["roles"])}
        for username, user in config["users"].items() if user["created"]
    ]
    return pd.DataFrame(users_data)