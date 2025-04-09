import streamlit as st

@st.fragment
def reset_side_selectbox(selectbox_key:list):
    """Reset the selectbox listed none."""
    for i in selectbox_key:
        st.session_state[i] = None
    st.session_state["selectbox_key"] = None

def click_on_user_sidebar_selectbox():
    reset_side_selectbox(["budget_key","requete_key"])
    if "derniere_ligne" in st.session_state:
        del st.session_state.derniere_ligne
    if "user_user_delete_mode" in st.session_state:
        st.session_state.user_delete_mode = "action"
    if "mode" in st.session_state:
        st.session_state.mode = "register"
    if "register_user_mode" in st.session_state:
        st.session_state.register_user_mode = "register"
    if "num_users_registered" in st.session_state:
        del st.session_state["num_users_registered"]

def click_on_budget_sidebar_selectbox():
    reset_side_selectbox(["users_key","requete_key"])

def click_on_requete_sidebar_selectbox():
    reset_side_selectbox(["users_key","budget_key"])

def user_selectbox():
    user_option_names = ["Créer","Modifier" ,"Supprimer","Liste"]
    user_selectbox = st.sidebar.selectbox("Utilisateur", user_option_names, index=None, key="users_key",on_change=click_on_user_sidebar_selectbox)
    return user_selectbox

def budget_selectbox():
    budget_option_names = ["Ajouter budget","Voir Budget"]
    budget_selectbox = st.sidebar.selectbox("Budget", budget_option_names, index=None, key="budget_key", on_change=click_on_budget_sidebar_selectbox)
    return budget_selectbox

def requete_selectbox():
    requete_option_names = ["Inserer requete","Modifier requete", "Supprimer requete"]
    requete_selectbox = st.sidebar.selectbox("Requete", requete_option_names, index=None, key="requete_key", on_change=click_on_requete_sidebar_selectbox)
    return requete_selectbox