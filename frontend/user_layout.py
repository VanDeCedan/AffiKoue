import streamlit as st
from streamlit_option_menu import option_menu
import auth_front as auth_front
import selectbox_logic as selectbox

#*********************************************Login*********************************************************
@st.dialog("Connexion")
def login_menu():
    st.markdown(
        """
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
        """,
        unsafe_allow_html=True,
    )

    with st.form("Login Form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")

        submitted = st.form_submit_button("Se connecter")
        if submitted:
            response = auth_front.login(username, password)
            if response.status_code == 200:
                st.session_state.token = response.json()["access_token"]
                st.session_state.user_roles = auth_front.get_user_roles(st.session_state.token)
                st.session_state.user_nom_prenoms = auth_front.get_user_nom(st.session_state.token)
                st.success("Connecté")
                st.rerun()  # Re-run the app to remove dialog and go to next screen
            else:
                st.error("Erreur de connexion")

#********************************************Register********************************************************

def register_fields(i):
    """Display the registration fields for user i."""
    st.markdown(
        """
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
        """,
        unsafe_allow_html=True,
    )

    st.title(f"Créer un compte utilisateur {i+1}")
    departement_options = ["DFA","DRHA","DMMC", "DSR/SMNI", "DRSE", "DAI", "DARS3","DHASE"]

    user_username = st.text_input("Username", key=f"username_{i}")
    user_nom_prenoms = st.text_input("Nom et prénoms", key=f"nom_prenoms_{i}")
    user_departement = st.selectbox("Departement", departement_options, index=None, key=f"departement_{i}")
    user_email = st.text_input("Email", key=f"email_{i}")
    user_password = st.text_input("Password", type="password", key=f"password_{i}")
    user_roles = st.selectbox("Roles", ["Admin", "Budget", "Comptable", "Users"], index=None, key=f"roles_{i}")

    if user_username and user_nom_prenoms and user_departement and user_email and user_password and user_roles:
        return user_username, user_nom_prenoms, user_departement, user_email, user_password, user_roles
    else:
        st.warning("Veuillez remplir tous les champs")
        return None, None, None, None, None, None

def stock_registered_infos():
    username= st.session_state.username_key
    nom_prenoms= st.session_state.nom_key
    departement= st.session_state.departement_key
    email= st.session_state.email_key
    roles = st.session_state.roles_key
    st.session_state.derniere_ligne = {"username": username, 
                                    "nom_prenoms": nom_prenoms,
                                    "departement": departement,
                                    "email": email, 
                                    "roles": roles}

def user_register_register_mode_callback():
    st.session_state.register_user_mode = "register"
    # Clean up all previous `user_saved_{i}` keys
    keys_to_delete = [key for key in st.session_state if key.startswith("user_saved_")]
    for key in keys_to_delete:
        del st.session_state[key]
    del st.session_state["num_users_registered"]

def user_register_show_mode_callback():
    st.session_state.register_user_mode = "show"

def reset_register_fields():
    num_users = st.session_state.get("num_users_to_register", 0)
    for i in range(num_users):
        for field in ["username", "nom_prenoms", "departement", "email", "password", "roles"]:
            key = f"{field}_{i}"
            if key in st.session_state:
                del st.session_state[key]
        if f"user_saved_{i}" in st.session_state:
            del st.session_state[f"user_saved_{i}"]
    st.session_state.user_register_data = []
    st.session_state.num_users_to_register = 0

def register_user_and_reset_callback():
    if not st.session_state.user_register_data:
        st.warning("Aucun utilisateur à enregistrer.")
        return

    for user_data in st.session_state.user_register_data:
        auth_front.register(
            user_data['username'],
            user_data['nom_prenoms'],
            user_data['departement'],
            user_data['email'],
            user_data['password'],
            user_data['roles']
        )
        st.success(f"{user_data['username']} enregistré avec succès ✅")
    # Clean up all previous `user_saved_{i}` keys
    keys_to_delete = [key for key in st.session_state if key.startswith("user_saved_")]
    for key in keys_to_delete:
        del st.session_state[key]
    del st.session_state["num_users_registered"]

    reset_register_fields()
    st.session_state.register_user_mode = "register"

def register_and_finish_callback():
    register_user_and_reset_callback()
    selectbox.reset_side_selectbox(["users_key"])

def init_user_register_session_state():
    defaults = {
        "register_user_mode": "register",
        "user_register_data": [],
        "num_users_to_register": 0,
        "num_users_registered" : 0
    }
    # Clean up all previous `user_saved_{i}` keys
    keys_to_delete = [key for key in st.session_state if key.startswith("user_saved_")]
    for key in keys_to_delete:
        del st.session_state[key]
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def register_user_menu():
    init_user_register_session_state()

    if st.session_state.register_user_mode == "register":
        num_users = st.number_input("Nombre d'utilisateur à enrégistrer", 
                                    min_value=1, step=1, key="num_users_to_register")

        if len(st.session_state.user_register_data) != num_users:
            st.session_state.user_register_data = [{} for _ in range(num_users)]

        for i in range(num_users):
            with st.container(border=True):
                user_data = register_fields(i)
                if all(user_data):  # Check that all fields are filled
                    if st.button(f"Sauvegarder utilisateur {i+1}", key=f"save_button_{i}"):
                        st.session_state.user_register_data[i] = {
                            "username": user_data[0],
                            "nom_prenoms": user_data[1],
                            "departement": user_data[2],
                            "email": user_data[3],
                            "password": user_data[4],
                            "roles": user_data[5],
                        }
                        if not st.session_state.get(f"user_saved_{i}", False):
                            st.session_state[f"user_saved_{i}"] = True
                            st.session_state["num_users_registered"] += 1
                        st.success(f"{user_data[0]} sauvegardé, veuillez valider à la fin")

        # Check if all users are saved
        if st.session_state["num_users_registered"] >= 1 and st.session_state["num_users_registered"] == num_users :
            st.button("Valider", on_click=user_register_show_mode_callback)
        st.info(f"Nombre d'utilisateurs sauvegardés : {st.session_state["num_users_registered"]}")

    elif st.session_state.register_user_mode == "show":
        if not st.session_state.user_register_data:
            st.warning("Aucune donnée utilisateur à afficher.")
            return

        for i, user in enumerate(st.session_state.user_register_data):
            with st.container(border=True):
                st.subheader(f"Utilisateur {i+1} : {user.get('username', 'N/A')}")
                st.info(f"Nom : {user.get('nom_prenoms', 'N/A')}")
                st.info(f"Département : {user.get('departement', 'N/A')}")
                st.info(f"Email : {user.get('email', 'N/A')}")
                st.info(f"Rôles : {user.get('roles', 'N/A')}")

        # Final buttons
        col1, col2, col3 = st.columns([2,4,2])
        with col1:
            st.button("Annuler", on_click=user_register_register_mode_callback)
        with col2:
            # Optional: Add another button to "Enregistrer et continuer"
            st.button("Enregistrer et ajouter nouveau", on_click=register_user_and_reset_callback)
        with col3:
            st.button("Enregistrer et finir", on_click=register_and_finish_callback)

#*****************************************Edit**********************************************************

def edit_users_menu(username_to_edit,context="modification"):
    if context == "registration":
        st.subheader(f"Editer un utilisateur {username_to_edit}:")
    modifications_list=["Roles", "Email", "Password", "Departement"]
    selected_modification=option_menu(menu_title="Modifier un utilisateur", options=modifications_list, 
                                            orientation="horizontal", default_index=0, menu_icon="person")
    return selected_modification

def edit_roles_menu(username_to_edit):
    new_role = st.selectbox("Nouveau role", ["Admin", "Budget", "Comptable" ,"Users"], index=None)
    if st.button("Modifier"):
        if username_to_edit:
            auth_front.update_user_info(username_to_edit, "roles", new_role)
            st.success(f"Nouveau rôle : {new_role} ")

def edit_email_menu(username_to_edit):
    new_email = st.text_input("Nouveau email")
    if st.button("Modifier"):
        if username_to_edit:
            auth_front.update_user_info(username_to_edit, "email", new_email)
            st.success(f"Nouveau email : {new_email} ")

def edit_password_menu(username_to_edit):
    new_password = st.text_input("Nouveau mot de passe", type="password")
    if st.button("Modifier"):
        if username_to_edit:
            auth_front.update_user_info(username_to_edit, "password", new_password)
            st.success(f"Nouveau mot de passe : {new_password} ")

def edit_department_menu(username_to_edit):
    new_departement = st.selectbox("Nouveau departement",
                                ["DFA","DRHA","DMMC", "DSR/SMNI", "DRSE", "DAI", "DARS3","DHASE"], index=None)
    if st.button("Modifier"):
        if username_to_edit:
            auth_front.update_user_info(username_to_edit, "departement", new_departement)
            st.success(f"Nouveau departement : {new_departement} ")

#***************************************delete****************************************************************

@st.fragment
def delete_user_callback():
    auth_front.delete_user(st.session_state.username_to_delete)
    st.session_state.delete_mode = "show"

def delete_user_menu():
    if "user_delete_mode" not in st.session_state:
        st.session_state.user_delete_mode = "action"
    if "username_to_delete" not in st.session_state:
        st.session_state.username_to_delete = None

    if st.session_state.user_delete_mode == "action":
        username_to_edit = st.selectbox("Sélectionner un utilisateur", auth_front.get_users_list(), index=None)
        if username_to_edit :
            st.session_state.username_to_delete = username_to_edit
        st.button("Supprimer", on_click=delete_user_callback)

    elif st.session_state.user_delete_mode == "show":
        if st.session_state.username_to_delete :
            st.success(f"Utilisateur {st.session_state.username_to_delete} supprimé avec succès")
            if st.button("Supprimer un autre utilisateur"):
                st.session_state.user_delete_mode = "action"
                st.session_state.username_to_delete = None
        else:
            st.session_state.user_delete_mode = "action"
            st.session_state.username_to_delete = None

#******************************************Liste***********************************************************
def show_budget_as_df():
    Username = st.selectbox("Sélectionner un utilisateur", auth_front.get_users_list(), index=None)
    df = auth_front.get_users_df(Username)
    st.dataframe(df)