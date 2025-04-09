import streamlit as st
import tempfile
import budget_front as bu_front

def upload_and_insert_budget(): 
    st.title("📝 Charger un budget Excel dans la base de données")

    uploaded_file = st.file_uploader("Choisir un fichier Excel", type=["xlsx"])

    if uploaded_file is not None:
        st.success(f"Fichier sélectionné : {uploaded_file.name}")
    
        if st.button("📥 Enrégistrer dans la base"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name
            result = bu_front.insert_budget_file(tmp_path)
            if "success" in result:
                st.success(result["success"])
            else:
                st.error(result.get("error", "Une erreur est survenue"))

def show_budget_as_df():
    Username = st.selectbox("Sélectionner un Projet", bu_front.get_projet_list(), index=None)
    df = bu_front.get_budget_df(Username)
    st.dataframe(df)