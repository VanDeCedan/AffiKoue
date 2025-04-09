from flask import Flask, request, jsonify 
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager,create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
import os
from backend.db import db, User
from backend.auth import put_register_user, put_update_user_infos, get_is_first_user, put_delete_user
import backend.budget as budget
import backend.requete as requete
import backend.dp as dp
from flask_cors import CORS
import backend.analyse as analyse

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("url")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = "your_jwt_secret_key"  # Change this to a random secret key

jwt=JWTManager(app)
db.init_app(app)

with app.app_context():
    db.create_all()

#*********************************General routes*******************************************

@app.route('/api/get_vals', methods=['GET'])
def route_get_vals():
    table_name = request.args.get("table_name")
    search_col = request.args.get("search_col")
    search_val = request.args.get("search_val")
    cols = request.args.getlist("cols")  # List of columns to retrieve
    if not all([table_name, search_col, search_val, cols]):
        return jsonify({"error": "Missing parameters"}), 400
    result = dp.get_vals(table_name, search_col, search_val, cols)
    if result is None:
        return jsonify({"error": "No matching data found"}), 404
    return jsonify(dict(zip(cols, result)))

@app.route('/api/last_row_infos', methods=['GET'])
def route_last_row_cols_infos():
    table_name = request.args.get("table_name")
    id_col = request.args.get("id_col")
    cols_to_retrieve = request.args.getlist("cols_to_retrieve")  # 👈 important
    result = dp.get_last_row_infos(table_name,id_col, cols_to_retrieve)
    return jsonify(result), 200



#*********************************Users routes*******************************************
@app.route('/api/register', methods=['POST'])
def route_register():
    try:
        data = request.get_json()
        user_username = data['user_username']
        user_nom_prenoms = data['user_nom_prenoms']
        user_departement = data['user_departement']
        user_email = data['user_email']
        user_password = data['user_password']
        user_roles = data['user_roles']

        # Debugging: Log the received data
        print(f"Received data: {data}")

        if put_register_user(user_username, user_nom_prenoms, user_departement, user_email, user_password, user_roles):
            return jsonify({"success": True}), 201
        else:
            return jsonify({"error": "L'utilisateur existe déjà"}), 409
    except Exception as e:
        # Log the error for debugging
        print(f"Error in /api/register: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/login', methods=['POST'])
def route_login():
    data= request.get_json()
    user = User.query.filter_by(user_username=data['user_username']).first()
    if user and check_password_hash(user.user_password, data['user_password']):
        access_token = create_access_token(identity=user.user_username)
        return jsonify(access_token=access_token), 200
    return jsonify({"error": "Mot de passe ou username invalide"}), 401

@app.route('/api/protected', methods=['GET'])
@jwt_required()
def route_protected():
    current_user = get_jwt_identity()
    user= User.query.filter_by(user_username=current_user).first()
    if user:
        return jsonify({
            "user": {
                "user_username": user.user_username,
                "user_nom_prenoms": user.user_nom_prenoms,
                "user_departement": user.user_departement,
                "user_email": user.user_email,
                "user_roles": user.user_roles
            }
            }), 200
    return jsonify({"error": "Utilisateur non retrouvé"}), 404

@app.route('/api/is_first_user', methods=['GET'])
def route_is_first_user():
    is_first = get_is_first_user()
    return jsonify({"is_first": is_first})

@app.route('/api/list_of_values', methods=['GET'])
def route_col_val_tolist():
    table_name = request.args.get('table_name')
    column_name = request.args.get('column_name')
    val_uniques = dp.get_col_vals_list(table_name, column_name)
    if val_uniques is not None:
        return jsonify({"values": val_uniques}), 200
    else:
        return jsonify({"error": "Aucune valeur touvée"}), 404

@app.route('/api/update_user_info', methods=['POST'])
def route_update_user_info():
    data = request.get_json()
    user_username = data.get('user_username')
    info_type = data.get('info_type')
    info_value = data.get('info_value')

    print(f"Updating {info_type} for {user_username} to {info_value}")
    result = put_update_user_infos(user_username, info_value, info_type)
    print(f"Update result: {result}")
    return jsonify({"success": result})

@app.route('/api/delete_user', methods=['POST'])
def route_delete_user_route():
    data = request.get_json()
    user_username = data.get('user_username')
    put_delete_user(user_username)
    return jsonify({"success": True})

@app.route('/api/get_users_table_as_df', methods=['GET'])
def route_get_users_table_as_df():
    users = dp.get_table_as_df("users", ["user_username", "user_nom_prenoms", "user_departement", "user_email", "user_roles"],
                            ["Username", "Nom et prénoms", "Département", "Email", "Roles"])
    return jsonify(users.to_dict(orient='records'))


#*********************************Budget routes*******************************************
@app.route('/api/insert_budget', methods=['POST'])
def route_insert_budget():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    result = (file)
    final_result = budget.put_inserer_budget(result)
    return jsonify(final_result)

@app.route('/api/calcul_depense_code_activite', methods=['GET'])
def route_calcul_depense():
    code_activite = request.args.get('budget_code_activite')
    depenses = budget.get_calculer_budget_depense(code_activite)
    return jsonify(depenses)

@app.route('/api/inserer_depenses', methods=['POST'])
def route_inserer_depenses():
    code_activite = request.args.get('budget_code_activite')
    result = budget.put_inserer_budget(code_activite)
    return jsonify(result)

@app.route('/api/calcul_solde_code_actvite', methods=['GET'])
def route_calcul_solde():
    code_activite = request.args.get('budget_code_activite')
    solde = budget.get_calculer_budget_solde(code_activite)
    return jsonify(solde)

@app.route('/api/inserer_solde', methods=['POST'])
def route_inserer_solde():
    code_activite = request.args.get('budget_code_activite')
    result = budget.put_inserer_solde(code_activite)
    return jsonify(result)

@app.route('/api/calcul_consommation_code_activite', methods=['GET'])
def route_calcul_consommation():
    code_activite = request.args.get('budget_code_activite')
    consommation = budget.get_calculer_budget_consommation(code_activite)
    return jsonify(consommation)

@app.route('/api/inserer_consommation', methods=['POST'])
def route_inserer_consommation():
    code_activite = request.args.get('budget_code_activite')
    result = budget.put_inserer_consommation(code_activite)
    return jsonify(result)

@app.route('/api/budget_as_df', methods=['GET'])
def route_budget_as_df():
    Projet = request.args.get('Projet')
    budget = dp.get_table_as_df("budget", ["budget_code_activite", "budget_code_projet", "budget_montant_initial", "budget_montant_depense", "budget_solde", "budget_consommation", "budget_projet"],
                            ["Code activité", "Code projet", "Montant initial", "Montant dépensé", "Solde", "Consommation", "Projet"])
    return jsonify(budget.to_dict(orient='records'))

#*********************************Requete routes*******************************************
@app.route('/api/code_derniere_requete', methods=['GET'])
def route_code_derniere_requete():
    return jsonify(requete.get_code_derniere_req())

@app.route('/api/nb_requete_complementaire', methods=['GET'])
def route_nb_requete_complementaire():
    code_requete = request.args.get('requete_code_requete_init')
    return jsonify(requete.get_nb_requete_cplmt(code_requete))

@app.route('/api/insert_requete', methods=['POST'])
def insert_requete_route():
    data = request.get_json()
    result = requete.put_insert_requete(data)
    return jsonify(result)

@app.route('/api/insert_activity', methods=['POST'])
def route_insert_activity():
    data = request.get_json()
    required_fields = ["requete_id", "requete_type_requete", "requete_code_requete_init", "requete_code_requete_cplmt", "requete_nom_activite", "requete_type_objet", "requete_demandeur", "requete_code_activite", "requete_montant", "requete_date", "requete_code_projet", "requete_code_resultat", "requete_item_code", "requete_departement", "requete_status"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400
    result = requete.put_inserer_req(**data)
    return jsonify(result), 201 if result["success"] else 400

@app.route("/api/update_requete_info", methods=['POST'])
def route_update_requete_info():
    data = request.get_json()
    required_fields = ["requete_id", "requete_info_name", "requete_info_value"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400
    result = requete.put_update_requete_info(**data)
    return jsonify(result), 200 if result["success"] else 400

@app.route('/api/delete_requete', methods=['POST'])
def route_delete_requete():
    data = request.get_json()
    required_fields = ["requete_id"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400
    result = requete.put_delete_requete(**data)
    return jsonify(result), 200 if result["success"] else 400

@app.route('/api/update_requete_status', methods=['POST'])
def route_update_requete_status():
    data = request.get_json()
    required_fields = ["requete_id", "requete_status"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400
    result = requete.put_update_requete_status(**data)
    return jsonify(result), 200 if result["success"] else 400

@app.route('/api/requete_as_df', methods=['GET'])
def route_requete_as_df():
    Projet = request.args.get('requete_projet')
    requetes = dp.get_table_as_df("requete", ["requete_code_requete_init", "requete_code_requete_cplmt", "requete_nom_activite", "requete_type_objet", "requete_demandeur", "requete_code_activite", "requete_montant", "requete_date", "requete_departement"],
                                ["Code requête initiale", "Code requête complémentaire", "Nom activité", "Type objet", "Demandeur", "Code activité", "Montant", "Date", "Département"])
    requetes = requetes[requetes["Projet"] == Projet]
    return jsonify(requetes.to_dict(orient='records'))

@app.route('/api/insert_reconciliation', methods=['POST'])
def route_insert_reconciliation():
    data = request.get_json()
    required_fields = ["reconciliation_id", "reconciliation_code_requete", "reconciliation_nom_activite", "reconciliation_code_activite", "reconciliation_code_projet", "reconciliation_code_resultat", "reconciliation_item_code", "reconciliation_montant"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400
    result = requete.put_inserer_reconciliation(**data)
    return jsonify(result), 201 if result["success"] else 400

@app.route('/api/update_reconciliation', methods=['POST'])
def route_update_reconciliation():
    data = request.get_json()
    required_fields = ["reconciliation_id", "reconciliation_nom_activite", "reconciliation_code_activite", "reconciliation_code_projet", "reconciliation_code_resultat", "reconciliation_item_code", "reconciliation_montant"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400
    result = requete.put_update_reconciliation(**data)
    return jsonify(result), 200 if result["success"] else 400

@app.route('/api/delete_reconciliation', methods=['POST'])
def route_delete_reconciliation():
    data = request.get_json()
    required_fields = ["reconciliation_id"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400
    result = requete.put_delete_reconciliation(**data)
    return jsonify(result), 200 if result["success"] else 400

@app.route('/api/reconciliation_as_df', methods=['GET'])
def route_reconciliation_as_df():
    Projet = request.args.get('reconciliation_projet')
    reconciliation = dp.get_table_as_df("reconciliation", ["reconciliation_code_requete", "reconciliation_nom_activite", "reconciliation_code_activite", "reconciliation_code_projet", "reconciliation_code_resultat", "reconciliation_item_code", "reconciliation_montant"],
                                        ["Code requête", "Nom activité", "Code activité", "Code projet", "Code résultat", "Item code", "Montant"])
    reconciliation = reconciliation[reconciliation["Projet"] == Projet]
    return jsonify(reconciliation.to_dict(orient='records'))

@app.route('/api/requete_non_reconcilie_df',methods=['GET'])
def route_requete_non_reconcilie_df():
    requete_non_reconcilie= analyse.get_df_requete_non_reconcile()
    return jsonify(requete_non_reconcilie.to_dict(orient='records'))

@app.route('/api/consomation_par_projet',methods=['GET'])
def route_consomation_par_projet():
    consomation_par_projet= analyse.get_consomation_par_projet()
    return jsonify(consomation_par_projet.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)