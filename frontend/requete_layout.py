import streamlit as st
from streamlit_option_menu import option_menu
import auth_front as auth_front
import selectbox_logic as selectbox
import requete_front as req_front
from datetime import datetime
import budget_front as bu_front

#*******************************Requete Initiale*********************************************
def requete_fields(i, type="Annulation de requete"):
    st.markdown("""
    <style>
    .stForm {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
    }
    form {
        width: 400px;
        margin: auto;
    }
    </style>
    """, unsafe_allow_html=True)

    results = {}

    if type == "Annulation de requete":
        requete_code_requete_cplmt = st.selectbox("Sélectionner l'identifiant de la requête", req_front.get_requete_code_requete_cplmt_list(),
                                index=None, key=f"req_id_{i}_{type}")
        if not requete_code_requete_cplmt:
            st.warning("Veuillez choisir l'identifiant pour continuer")
            return None
        results["requete_code_requete_cplmt"] = requete_code_requete_cplmt
        results["requete_id"] = requete_code_requete_cplmt+"Annule"

        columns_to_retrieve = [
            "requete_type_requete",
            "requete_code_requete_init",
            "requete_nom_activite",
            "requete_type_objet",
            "requete_demandeur",
            "requete_code_activite",
            "requete_montant_avance_voyage",
            "requete_montant_achat",
            "requete_montant_momo",
            "requete_montant"]
        fetched = req_front.get_cols_vals(
            table_name="requete",
            search_col="requete_code_requete",
            search_val=requete_code_requete_cplmt,
            cols=columns_to_retrieve
        )
        if "error" in fetched:
            st.error(f"Erreur lors de la récupération des données : {fetched['error']}")
            return None
        results.update(fetched)

        results["requete_date"]=datetime.now()
        results["requete_status"] = "Annule"

        return results

    else :
        # Normal request or complémentaire
        requete_objet_options = ["Avance de voyage", "Achat", "Momo"]

        requete_type_objet = st.multiselect("Types d'objets de la requête", requete_objet_options,
                                            ["Avance de voyage", "Achat"], key=f"requete_type_objet_{i}_{type}")
        requete_nom_activite = st.text_input("Nom de l'activité", key=f"req_nom_activite_{i}_{type}")
        requete_demandeur = st.selectbox("Sélectionner le demandeur", auth_front.get_users_list(),
                                        index=None, key=f"req_demandeur_{i}_{type}")
        requete_code_activite = st.selectbox("Sélectionner un code activité", req_front.get_code_activite_list(),
                                            index=None, key=f"req_code_activite_{i}_{type}")
        
        if not (requete_type_objet and requete_nom_activite and requete_demandeur and requete_code_activite):
            st.warning("Veuillez saisir toutes les informations")
            return None

        results.update({
            "requete_type_objet": requete_type_objet,
            "requete_nom_activite": requete_nom_activite,
            "requete_demandeur": requete_demandeur,
            "requete_code_activite": requete_code_activite
        })

        results["requete_date"]=datetime.now().strftime("%Y-%m-%d")
        results["requete_status"] = "En cours"

        if type == "Requete initiale" :
            results["requete_code_requete_init"]=req_front.get_code_derniere_requete()
            results["requete_code_requete_cplmt"] = str(results["requete_code_requete_init"])
            results["requete_id"] = str(results["requete_code_requete_init"])

        if type == "Requete complémentaire":
            requete_code_requete_init = st.selectbox("Sélectionner le code de la requête principale", 
                                                    req_front.get_code_requete_list(), 
                                                    index=None, key=f"req_id_{i}_{type}")
            if not requete_code_requete_init:
                st.warning("Veuillez saisir toutes les informations")
                return None
            results["requete_code_requete_init"]  = requete_code_requete_init
            results["requete_code_requete_cplmt"] = str(requete_code_requete_init) + str(req_front.get_nb_requete_complementaire(requete_code_requete_init))
            results["requete_id"]=results["requete_code_requete_cplmt"]

# Set default values
        results["requete_montant_avance_voyage"] = 0
        results["requete_montant_achat"] = 0
        results["requete_montant_momo"] = 0

        if "Avance de voyage" in requete_type_objet:
            requete_montant_avance_voyage = st.number_input("Montant de l'avance de voyage", min_value=1, step=1,
                                    key=f"req_montant_avance_{i}_{type}")
            results["requete_montant_avance_voyage"] = requete_montant_avance_voyage

        if "Achat" in requete_type_objet:
            requete_montant_achat = st.number_input("Montant de l'achat", min_value=1, step=1,
                                    key=f"req_montant_achat_{i}_{type}")
            results["requete_montant_achat"] = requete_montant_achat

        if "Momo" in requete_type_objet:
            requete_montant_momo = st.number_input("Montant Momo", min_value=1, step=1,
                                    key=f"req_montant_momo_{i}_{type}")
            results["requete_montant_momo"] = requete_montant_momo

        results["requete_montant"]=results["requete_montant_momo"]+results["requete_montant_achat"] + results["requete_montant_avance_voyage"]      

    return results

def requete_register_register_mode_callback():
    if "num_requetes_registered" in st.session_state:
        st.session_state.register_requete_mode = "register"
    # Clean up all previous `user_saved_{i}` keys
    keys_to_delete = [key for key in st.session_state if key.startswith("requetes_saved_")]
    for key in keys_to_delete:
        del st.session_state[key]
    del st.session_state["num_requetes_registered"]

def requete_register_show_mode_callback():
    st.session_state.register_requete_mode = "show"

def reset_register_fields(type):
    if "num_requetes_registered" in st.session_state:
        num_requetes = st.session_state.get("num_requetes_to_register", 0)
    for i in range(num_requetes):
        req_field_list=["requete_code_requete_cplmt",
                        "requete_type_objet",
                        "requete_nom_activite",
                        "requete_demandeur",
                        "requete_code_activite",
                        "requete_code_requete_init",
                        "requete_montant_avance_voyage",
                        "requete_montant_achat",
                        "requete_montant_momo"]
        for field in req_field_list :
            key = f"{field}_{i}_{type}"
            if key in st.session_state:
                del st.session_state[key]
        if f"requetes_saved_{i}" in st.session_state:
            del st.session_state[f"requetes_saved_{i}"]
    st.session_state.requete_register_data = []
    st.session_state.num_requetes_registered = 0

def init_requete_register_session_state():
    defaults = {
        "register_requete_mode": "register",
        "requete_register_data": [],
        "num_requetes_to_register": 0,
        "num_requetes_registered" : 0
    }
    # Clean up all previous `user_saved_{i}` keys
    keys_to_delete = [key for key in st.session_state if key.startswith("requetes_saved_")]
    for key in keys_to_delete:
        del st.session_state[key]
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def requete_submission(results,code_activite):
    req_front.submit_requete(results)
    bu_front.get_depense_par_activite(code_activite)
    bu_front.post_inserer_depense(code_activite)
    bu_front.get_solde_par_activite(code_activite)
    bu_front.post_inserer_solde(code_activite)
    bu_front.get_consommation_par_activite(code_activite)
    bu_front.post_inserer_consommation(code_activite)

def get_solde(code_activite):
    solde = req_front.get_cols_vals("budget","budget_code_activite",code_activite,["budget_solde"])
    return solde