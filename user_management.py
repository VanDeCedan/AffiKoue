import sqlite3
from data import conn
from authentication import hash_password
import pandas as pd
import streamlit as st

DB_FILE = "users.db"

def register_user(username, nom, departement, email, password, roles):
    """Register a new user with hashed password."""
    con, c = conn()
    hashed_password = hash_password(password)
    try:
        c.execute("INSERT INTO users (username, nom, departement, email, password, roles) VALUES (?, ?, ?, ?, ?, ?)", 
                       (username, nom, departement, email, hashed_password, roles))
        con.commit()
    except sqlite3.IntegrityError:
        st.error("Cet utilisateur existe déjà")
    con.close()

def charger_all_users():
    """charger tout les utilisateurs dans un dataframe"""
    con, _ = conn()
    df = pd.read_sql("SELECT * FROM users", con)
    con.close()
    return df

def update_user_roles(username, roles):
    """Update user roles."""
    con, c = conn()
    c.execute("UPDATE users SET roles=? WHERE username=?", (roles, username))
    con.commit()
    con.close()

def update_user_password(username, new_password):
    """Update user password."""
    con, c = conn()
    hashed_password = hash_password(new_password)
    c.execute("UPDATE users SET password=? WHERE username=?", (hashed_password, username))
    con.commit()
    con.close()

def update_user_email(username, new_email):
    """Update user email."""
    con, c = conn()
    c.execute("UPDATE users SET email=? WHERE username=?", (new_email, username))
    con.commit()
    con.close()

def get_user_roles(username):
    """Get user roles."""
    con, c = conn()
    c.execute("SELECT roles FROM users WHERE username=?", (username,))
    roles = c.fetchone()[0]
    con.close()
    return roles

def delete_user(username):
    """Delete a user by username."""
    con, c = conn()
    c.execute("DELETE FROM users WHERE username=?", (username,))
    con.commit()
    con.close()