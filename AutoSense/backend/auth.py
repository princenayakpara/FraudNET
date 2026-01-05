import sqlite3
import hashlib
import secrets
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter()

DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password_hash TEXT, token TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (username TEXT, action TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

init_db()

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str

def hash_pw(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/api/auth/register")
def register(user: UserRegister):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (user.username, hash_pw(user.password), ""))
        conn.commit()
        return {"success": True, "message": "User registered"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")
    finally:
        conn.close()

@router.post("/api/auth/login")
def login(user: UserLogin):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password_hash=?", (user.username, hash_pw(user.password)))
    data = c.fetchone()
    if data:
        # Generate simple token
        token = secrets.token_hex(16)
        c.execute("UPDATE users SET token=? WHERE username=?", (token, user.username))
        conn.commit()
        conn.close()
        return {"success": True, "token": token, "username": user.username}
    else:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/api/auth/me")
def get_me(token: str):
    user = get_current_user(token)
    return {"username": user}

def get_current_user(token: str = None):
    if not token:
        raise HTTPException(status_code=401, detail="Token missing")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE token=?", (token,))
    data = c.fetchone()
    conn.close()
    if data:
        return data[0]
    raise HTTPException(status_code=401, detail="Invalid or expired token")
