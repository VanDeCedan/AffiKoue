from backend.db import db_connect
import pandas as pd
import backend.dp as dp

def put_inserer_budget(xlsx_file):
    """Insérer les données d'un budget chargé depuis excel dans la base."""
    engine = db_connect()
    if engine is None:
        return {"erreur" :"Impossible de se connecter à la base"}
    df = pd.read_excel(xlsx_file)
    df.columns = df.columns.str.replace(" ","").str.strip()
    try:
        df.to_sql("budget", engine, if_exists="append", index=False)
        return {"success": f"{len(df)} activités insérées dans la base"}
    except Exception as e:
        return {"error": str(e)}

def get_calculer_budget_depense(code_activite):
    engine = db_connect()  # Get the SQLAlchemy engine
    if engine is None:
        return None
    with engine.connect() as conn:  # Use SQLAlchemy's connection context
        # Load data into DataFrames
        df_budget = pd.read_sql("SELECT * FROM budget", conn)
        df_requete = pd.read_sql("SELECT * FROM requete", conn)
        df_reconciliation = pd.read_sql("SELECT * FROM reconciliation", conn)

        df_req_non_reconcilie = df_requete[
            ~df_requete["requete_code_requete_init"].isin(df_reconciliation["reconciliation_code_requete"])
        ]
        df_req_non_reconcilie = df_req_non_reconcilie[["requete_code_requete_init", "requete_code_activite", "requete_montant"]].rename(
            columns={
                "requete_code_requete_init": "code_requete",
                "requete_code_activite": "code_activite",
                "requete_montant": "montant"
            }
        )
        df_reconciliation = df_reconciliation[["reconciliation_code_requete", "reconciliation_code_activite", "reconciliation_montant"]].rename(
            columns={
                "reconciliation_code_requete": "code_requete",
                "reconciliation_code_activite": "code_activite",
                "reconciliation_montant": "montant"
            }
        )

        df_depenses = pd.concat([df_req_non_reconcilie, df_reconciliation], axis=0)

        # Map expenses to budget activities
        df_budget["budget_montant_depense"] = df_budget["budget_code_activite"].map(
            df_depenses.groupby("code_activite")["montant"].sum()
        )

        # Montant dépensé pour ce code activite
        montant_depense = df_budget[df_budget["budget_code_activite"] == code_activite]["budget_montant_depense"].values[0]
        return {"montant_depense": montant_depense}

def put_inserer_montant_depense(code_activite, montant_depense):
    """Mettre à jour le montant dépensé pour une activité donnée dans la base de données."""
    engine = db_connect()
    if engine is None:
        return {"erreur": "Impossible de se connecter à la base"}
    try:
        with engine.connect() as conn:
            # Update the budget table
            query = """
                UPDATE budget
                SET budget_montant_depense = :montant_depense
                WHERE budget_code_activite = :code_activite
            """
            conn.execute(query, {"montant_depense": montant_depense, "code_activite": code_activite})
        return {"success": f"Montant dépensé mis à jour pour le code activité : {code_activite}"}
    except Exception as e:
        return {"error": str(e)}

def get_calculer_budget_solde(code_activite):
    """ calculer le solude pour le code activité """
    engine = db_connect()  # Get the SQLAlchemy engine
    if engine is None:
        return None
    with engine.connect() as conn:  # Use SQLAlchemy's connection context
        # Load data into DataFrames
        df_budget = pd.read_sql("SELECT * FROM budget", conn)
        df_budget = df_budget[df_budget["budget_code_activite"] == code_activite]
        # Calculate the balance
        balance = df_budget["budget_montant_initial"].values[0] - df_budget["budget_montant_depense"].values[0]
        return {"solde": balance}

def put_inserer_solde(code_activite):
    """Mettre à jour le solde pour une activité donnée dans la base de données."""
    engine = db_connect()
    if engine is None:
        return {"erreur": "Impossible de se connecter à la base"}
    try:
        with engine.connect() as conn:
            # Update the budget table
            query = """
                UPDATE budget
                SET budget_solde = :solde
                WHERE budget_code_activite = :code_activite
            """
            conn.execute(query, {"solde": get_calculer_budget_solde(code_activite)["solde"], "code_activite": code_activite})
        return {"success": f"Solde mis à jour pour le code activité : {code_activite}"}
    except Exception as e:
        return {"error": str(e)}

def get_calculer_budget_consommation(code_activite):
    """ calculer la consommation pour le code activité """
    engine = db_connect()  # Get the SQLAlchemy engine
    if engine is None:
        return None
    with engine.connect() as conn:  # Use SQLAlchemy's connection context
        # Load data into DataFrames
        df_budget = pd.read_sql("SELECT * FROM budget", conn)
        df_budget = df_budget[df_budget["budget_code_activite"] == code_activite]
        # Calculate the consumption
        consumption = df_budget["budget_montant_depense"].values[0] / df_budget["budget_montant_initial"].values[0]
        return {"consommation": consumption}

def put_inserer_consommation(code_activite):
    """Mettre à jour la consommation pour une activité donnée dans la base de données."""
    engine = db_connect()
    if engine is None:
        return {"erreur": "Impossible de se connecter à la base"}
    try:
        with engine.connect() as conn:
            # Update the budget table
            query = """
                UPDATE budget
                SET budget_consommation = :consommation
                WHERE budget_code_activite = :code_activite
            """
            conn.execute(query, {"consommation": get_calculer_budget_consommation(code_activite)["consommation"], "code_activite": code_activite})
        return {"success": f"Consommation mise à jour pour le code activité : {code_activite}"}
    except Exception as e:
        return {"error": str(e)}