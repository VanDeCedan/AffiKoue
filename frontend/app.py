import streamlit as st
from streamlit_option_menu import option_menu
import auth_front as auth_front
import os
from dotenv import load_dotenv
import user_layout as user_ly
import budget_layout as bu_ly
import requete_layout as req_ly
import selectbox_logic as selectbox

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5000")  # Default to local backend

def main():
    st.markdown("<h1 style='text-align: center; color: green;'>SUIVI BUDGETAIRE</h1>", unsafe_allow_html=True)

    if "token" not in st.session_state:

        if auth_front.is_first_user():
            st.warning("Pas de compte existant, veuillez créer le compte admin")
            user_ly.register_user_menu()
        else :
            user_ly.login_menu()

    elif "token" in st.session_state:
        st.sidebar.title(f"Bienvenue \n {st.session_state.user_nom_prenoms}")
        roles= st.session_state.user_roles

        if "Admin" == roles:
            user_selectbox = selectbox.user_selectbox()
            budget_selectbox = selectbox.budget_selectbox()
            requete_selectbox = selectbox.requete_selectbox()

            if user_selectbox == "Créer":
                user_ly.register_user_menu()

            elif user_selectbox == "Modifier":
                username_to_edit = st.selectbox("Sélectionner un utilisateur", auth_front.get_users_list(), index=None)
                selected_modification= user_ly.edit_users_menu(username_to_edit)
                if selected_modification == "Roles":
                    user_ly.edit_roles_menu(username_to_edit)
                elif selected_modification == "Email":
                    user_ly.edit_email_menu(username_to_edit)
                elif selected_modification == "Password":
                    user_ly.edit_password_menu(username_to_edit)
                elif selected_modification == "Departement":
                    user_ly.edit_department_menu(username_to_edit)

            elif user_selectbox == "Supprimer":
                user_ly.delete_user_menu()
            
            elif user_selectbox == "Liste":
                user_ly.show_budget_as_df()

#*******************************************************Budget***************************************************************
            elif budget_selectbox == "Ajouter budget":
                bu_ly.upload_and_insert_budget()
            elif budget_selectbox == "Voir Budget":
                bu_ly.show_budget_as_df()

#**************************************************Requete******************************************************************
            elif requete_selectbox == "Inserer requete":
                req_ly.init_requete_register_session_state()
                if st.session_state.register_requete_mode == "register":
                    type_requete = st.selectbox("Type de requête",
                                                ["Requete initiale", "Requete complémentaire","Annulation de requete"],
                                            index=None,key="type_requete")
                    if type_requete :
                        num_requetes = st.number_input("Nombre de codes activités à enrégistrer",min_value=1,step=1)
                        if len(st.session_state.requete_register_data) != num_requetes:
                            st.session_state.requete_register_data = [{} for _ in range(num_requetes)]

                        for i in range(num_requetes):
                            with st.container(border=True):
                                user_data = req_ly.requete_fields(i,type_requete)
                                if all(val not in (None, "") for val in user_data.values()):
                                    if st.button(f"Sauvegarder la requete {i+1}", key=f"save_requete_button_{i}"):
                                        st.session_state.requete_register_data[i] = user_data
                                        if not st.session_state.get(f"requetes_saved_{i}", False):
                                            st.session_state[f"requetes_saved_{i}"] = True
                                            st.session_state["num_requetes_registered"] += 1
                                        st.success(f"sauvegardé, veuillez valider à la fin")

                        if st.session_state["num_requetes_registered"] >= 1 and st.session_state["num_requetes_registered"] == num_requetes :
                            st.button("Valider", on_click=req_ly.requete_register_show_mode_callback)

                        st.info(f"Nombre de code activités sauvegardés : {st.session_state["num_requetes_registered"]}")
                elif st.session_state.register_requete_mode == "show":
                    if not st.session_state.register_requete_mode:
                        st.warning("Aucune donnée utilisateur à afficher.")
                        return

                    for i, requete in enumerate(st.session_state.requete_register_data):
                        with st.container(border=True):
                            st.subheader(f"Requete  : {requete.get('requete_nom_activite', 'N/A')}")
                            st.info(f"Code activité : {requete.get('requete_code_activite', 'N/A')}")
                            st.info(f"Demandeur     : {requete.get('requete_demandeur', 'N/A')}")
                            st.info(f"Montant       : {requete.get('requete_montant', 'N/A')}")

                    # Final buttons
                    def register_requete_and_reset_callback():
                        if not st.session_state.requete_register_data:
                            st.warning("Aucune requête à enregistrer.")
                            return
                        # register in data base
                        for requete_data in st.session_state.requete_register_data:
                            req_ly.requete_submission(requete_data,requete_data["requete_code_activite"])
                            solde= req_ly.get_solde(requete_data["requete_code_activite"])
                            st.success(f" solde de la ligne {requete_data['requete_code_activite']} : {solde} ✅")
                        # Clean up all previous `user_saved_{i}` keys
                        keys_to_delete = [key for key in st.session_state if key.startswith("requetes_saved_")]
                        for key in keys_to_delete:
                            del st.session_state[key]
                        del st.session_state["num_requetes_registered"]
                        # reset field and go back to register mode
                        req_ly.reset_register_fields()
                        st.session_state.register_requete_mode = "register"

                    def register_requete_and_finish_callback():
                        register_requete_and_reset_callback()
                        selectbox.reset_side_selectbox(["requete_key"])

                    col1, col2, col3 = st.columns([2,4,2])
                    with col1:
                        st.button("Annuler", on_click=req_ly.requete_register_register_mode_callback)
                    with col2:
                        # Optional: Add another button to "Enregistrer et continuer"
                        st.button("Enregistrer et ajouter nouveau", on_click=register_requete_and_reset_callback)
                    with col3:
                        st.button("Enregistrer et finir", on_click=register_requete_and_finish_callback)

        if st.sidebar.button("Deconnexion",icon=":material/logout:"):
            del st.session_state.token
            del st.session_state.user_roles
            del st.session_state.user_nom_prenoms
            st.success("Déconnecté")
            st.rerun()

if __name__ == "__main__":
    main()
