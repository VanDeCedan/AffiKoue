import yaml
import streamlit as st
import streamlit_authenticator as stauth
from pathlib import Path

CONFIG_PATH = Path("config/config.yaml")

def load_config():
    """Charge la configuration YAML"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as file:
            return yaml.safe_load(file)
    return {"users": {}}

def save_config(config):
    """Sauvegarde la configuration YAML"""
    with open(CONFIG_PATH, "w") as file:
        yaml.dump(config, file)

def authenticate():
    """Gère l’authentification des utilisateurs"""
    config = load_config()
    
    if not config["users"]["admin"]["created"]:
        st.warning("Créez d'abord votre compte administrateur.")
        name = st.text_input("Nom & Prenoms")
        department = st.text_input("Departement")
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        roles = st.multiselect("Roles", ["users", "budget", "requete", "reconciliation", "dashboard"])

        if st.button("Créer mon compte"):
            hashed_password = stauth.Hasher([password]).hash(password)
            config["users"]["admin"] = {
                "name": name, "department": department, "username": username,
                "password": hashed_password, "roles": roles, "created": True
            }
            save_config(config)
            st.success("Compte administrateur créé. Redémarrez l'application.")

        st.stop()

    credentials = {
        "usernames": {
            user_data["username"]: {
                "name": user_data["name"],
                "password": user_data["password"],
                "roles": user_data["roles"]
            }
            for user_data in config["users"].values() if user_data["created"]
        }
    }

    authenticator = stauth.Authenticate(credentials, "app_cookie", "abcdef", cookie_expiry_days=1)
    name, authentication_status, username = authenticator.login("main")

    if authentication_status:
        return name, username, config["users"][username]["roles"]
    elif authentication_status == False:
        st.error("Nom d'utilisateur ou mot de passe incorrect")
    return None, None, None
