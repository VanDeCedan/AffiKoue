from sqlalchemy import text
import pandas as pd
from backend.db import db_connect, psycopg2_connect

def get_col_vals_list(table_name, column_name):
    """ Lise des valeurs distinctes d'une colonne d'une table """
    conn = psycopg2_connect()  # Returns a psycopg2 connection
    if conn is None:
        return None
    cur = conn.cursor()
    cur.execute(f"SELECT DISTINCT {column_name} FROM {table_name}")
    val_uniques = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return val_uniques

def get_vals(table_name, search_col, search_val, cols: list):
    """ Récupérer les valeurs dans chaque colonne en fonction de la valeur d'une autre colonne d'une même table """
    engine = db_connect()  # Get the SQLAlchemy engine
    if engine is None:
        return None
    col_str = ", ".join(cols)  # Join the column names into a string
    query = f"SELECT {col_str} FROM {table_name} WHERE {search_col} = :search_val"  # Use named parameters for SQLAlchemy
    with engine.connect() as conn:  # Use SQLAlchemy's connection context
        result = conn.execute(query, {"search_val": search_val}).fetchone()  # Execute the query and fetch one row
    return list(result) if result else None

def get_last_row_infos(tablename, id_col ,cols_to_retrieve:list):
    """ Récupérer les valeurs de la dernière ligne d'une table """
    engine = db_connect()  # Get the SQLAlchemy engine
    if engine is None:
        return None

    col_str = ", ".join(cols_to_retrieve)
    query = f"SELECT {col_str} FROM {tablename} ORDER BY {id_col} DESC LIMIT 1"

    with engine.connect() as conn:
        result = conn.execute(text(query)).fetchone()

    return list(result) if result else None

def put_inserer_valeurs(table_name, table_cols: list, values: list):
    """ Insérer des valeurs dans une table """
    engine = db_connect()  # Get the SQLAlchemy engine
    if engine is None:
        return None
    col_str = ", ".join(table_cols)  # Join column names into a string
    placeholders = ", ".join([f":{col}" for col in table_cols])  # Use named placeholders for SQLAlchemy
    query = f"INSERT INTO {table_name} ({col_str}) VALUES ({placeholders})"
    with engine.connect() as conn:  # Use SQLAlchemy's connection context
        try:
            conn.execute(query, {col: val for col, val in zip(table_cols, values)})  # Map columns to values
            return {"success": "Values inserted successfully"}
        except Exception as e:
            return {"error": str(e)}

def get_table_as_df(table, colnames_in_table: list, colnames_in_df: list):
    engine = db_connect()  # Get the SQLAlchemy engine
    if engine is None:
        return None
    with engine.connect() as conn:  # Use SQLAlchemy's connection context
        # Retrieve data from the table
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
        # Select and rename columns
        df_f = df[colnames_in_table].copy()
        df_f.columns = colnames_in_df
    return df_f

def get_convertir_df_excel(df):
    """ Convertir dataframe en fichier Excel """
    excel_file = df.to_excel(index=False)
    return excel_file