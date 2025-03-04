import bcrypt
from data import conn

def hash_password(password):
    """Hash the password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed_password):
    """Verify a password against its hashed version."""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def is_first_user():
    """Check if the users table is empty."""
    con, c = conn()
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    con.close()
    return count == 0

def charger_user_info(username):
    """charger les informations d'un utilisateur"""
    con, c = conn()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user_data = c.fetchone()
    con.close()
    return user_data