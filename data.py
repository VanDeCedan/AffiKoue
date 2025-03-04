import sqlite3 as sql

# connection à la base de données
def conn():
    con = sql.connect("data/finance.db")
    c = con.cursor()
    return con, c

# création des tables
def creer_tables():
    con, c = conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS budget (b_code_activite INTEGER PRIMARY KEY, 
    b_projet TEXT,b_code_resultat TEXT,b_item_code TEXT,b_montant INTEGER, b_depense INTEGER,
    solde INTEGER,b_departement TEXT)
    ;
    CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, nom TEXT, departement TEXT, email TEXT, password TEXT, roles TEXT)
    ;
    CREATE TABLE IF NOT EXISTS requete (id TEXT PRIMARY KEY,id_requete TEXT,type_activite TEXT,
    nom TEXT,code_requete INTEGER,type_requete TEXT,demandeur TEXT,r_code_activite INTEGER,
    r_montant INTEGER,date DATETIME DEFAULT CURRENT_TIMESTAMP,r_projet TEXT,r_code_resultat TEXT,r_item_code TEXT,r_departement TEXT)
    """)
    con.commit()  # enregistrer
    con.close()  # fermer la connection
