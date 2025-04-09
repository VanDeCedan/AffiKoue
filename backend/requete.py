from backend.db import db_connect, Requete, db, Reconciliation
import pandas as pd
import backend.dp as dp

def get_code_derniere_req():
    """ recupérer le code de la dernière requête enrégistrée dans la base"""
    engine = db_connect()  # Get the SQLAlchemy engine
    if engine is None:
        return None
    query = """SELECT MAX(code_requete) FROM requete WHERE type_activite='Requête initiale'"""
    with engine.connect() as conn:  # Use SQLAlchemy's connection context
        result = conn.execute(query).scalar()  # Use scalar() to fetch a single value
    return result if result else 999

def get_nb_requete_cplmt(code_requete):
    """ Récupérer le nombre de requêtes complémentaires pour un code de requête donné """
    engine = db_connect()  # Get the SQLAlchemy engine
    if engine is None:
        return None
    query = """SELECT COUNT(*) FROM requete 
            WHERE code_requete = :code_requete 
            AND type_activite = 'Requête complémentaire'"""
    with engine.connect() as conn:  # Use SQLAlchemy's connection context
        result = conn.execute(query, {"code_requete": code_requete}).scalar()  # Use scalar() to fetch the count
    return result if result else 0

def put_insert_requete(data):
    try:        
        requete = Requete(**data)
        db.session.add(requete)
        db.session.commit()
        return {"success": True, "message": "Requête insérée avec succès"}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": f"Erreur : {str(e)}"}

def put_inserer_req(requete_id,requete_type_requete ,requete_code_requete_init, requete_code_requete_cplmt, requete_nom_activite, requete_type_objet, requete_demandeur, requete_code_activite, requete_montant, requete_date, requete_code_projet, requete_code_resultat, requete_item_code, requete_departement,requete_status):
    """ Insérer une nouvelle requête dans la base de données """
    engine = db_connect()  # Get the SQLAlchemy engine
    if engine is None:
        return {"erreur" :"Impossible de se connecter à la base"}
    df = pd.DataFrame({
        "requete_id": [requete_id],
        "requete_type_requete": [requete_type_requete],
        "requete_code_requete_init": [requete_code_requete_init],
        "requete_code_requete_cplmt": [requete_code_requete_cplmt],
        "requete_nom_activite": [requete_nom_activite],
        "requete_type_objet": [requete_type_objet],
        "requete_demandeur": [requete_demandeur],
        "requete_code_activite": [requete_code_activite],
        "requete_montant": [requete_montant],
        "requete_date": [requete_date],
        "requete_code_projet": [requete_code_projet],
        "requete_code_resultat": [requete_code_resultat],
        "requete_item_code": [requete_item_code],
        "requete_departement": [requete_departement],
        "requete_status": [requete_status]
    })
    try:
        df.to_sql("requete", engine, if_exists="append", index=False)
        return {"success": f"requête {requete_nom_activite} enrégistrée avec succès"}
    except Exception as e:
        return {"error": str(e)}

def put_update_requete_info(requete_id, infos, info_type):
    code_requete = Requete.query.filter_by(requete_id=requete_id).first()
    if not code_requete:
        return False
    setattr(code_requete, info_type, infos)
    db.session.commit()
    return True

def put_delete_requete(requete_id):
    requete= Requete.query.filter_by(requete_id=requete_id).first()
    if requete :
        db.session.delete(requete)
        db.session.commit()
        return True
    return False

def put_update_requete_status(requete_code_requete):
    """ Mettre à jour le status de la requete"""
    # chercher si le code requete est dans la table reconciliation
    engine = db_connect()  # Get the SQLAlchemy engine
    if engine is None:
        return None
    query = f"""SELECT COUNT(*) FROM reconciliation
            WHERE reconciliation_code_requete = :{requete_code_requete}"""
    with engine.connect() as conn:  # Use SQLAlchemy's connection context
        result = conn.execute(query, {requete_code_requete: requete_code_requete}).scalar()  # Use scalar() to fetch the count
    if result == 0:
        # mettre à jour le status de la requete dans la table requete
        requete = Requete.query.filter_by(requete_code_requete=requete_code_requete).first()
        if not requete:
            return False
        Requete.requete_status = "En cours"
        db.session.commit()
        return True
    elif result >= 1:
        # mettre à jour le status de la requete dans la table requete
        requete = Requete.query.filter_by(requete_code_requete=requete_code_requete).first()
        if not requete:
            return False
        Requete.requete_status = "Reconciliée"
        db.session.commit()
        return True


def put_inserer_reconciliation(reconciliation_id, reconciliation_code_requete, reconciliation_nom_activite ,reconciliation_code_activite, reconciliation_code_projet, reconciliation_code_resultat, reconciliation_item_code, reconciliation_montant):
    """ Insérer une nouvelle réconciliation dans la base de données """
    engine = db_connect()  # Get the SQLAlchemy engine
    if engine is None:
        return {"erreur" :"Impossible de se connecter à la base"}
    df = pd.DataFrame({
        "reconciliation_id": [reconciliation_id],
        "reconciliation_code_requete": [reconciliation_code_requete],
        "reconciliation_nom_activite": [reconciliation_nom_activite],
        "reconciliation_code_activite": [reconciliation_code_activite],
        "reconciliation_code_projet": [reconciliation_code_projet],
        "reconciliation_code_resultat": [reconciliation_code_resultat],
        "reconciliation_item_code": [reconciliation_item_code],
        "reconciliation_montant": [reconciliation_montant]
    })
    try:
        df.to_sql("reconciliation", engine, if_exists="append", index=False)
        return {"success": f"réconciliation {reconciliation_id} enrégistrée avec succès"}
    except Exception as e:
        return {"error": str(e)}

def put_update_reconciliation_info(reconciliation_id, infos, info_type):
    reconciliation = Reconciliation.query.filter_by(reconciliation_id=reconciliation_id).first()
    if not reconciliation:
        return False
    setattr(reconciliation, info_type, infos)
    db.session.commit()
    return True

def put_delete_reconciliation(reconciliation_id):
    reconciliation= Reconciliation.query.filter_by(reconciliation_id=reconciliation_id).first()
    if reconciliation :
        db.session.delete(reconciliation)
        db.session.commit()
        return True
    return False