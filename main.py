import sqlite3
from contextlib import contextmanager
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

app = FastAPI()

# Configuración de base de datos
DB_FILE = 'database.sqlite'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS areas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_area TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_completo TEXT NOT NULL,
                rol TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                codigo_patrimonial TEXT NOT NULL,
                categoria TEXT NOT NULL,
                descripcion TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                type TEXT NOT NULL,
                persona_id INTEGER,
                area_id INTEGER,
                observaciones TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES items (id),
                FOREIGN KEY (persona_id) REFERENCES personas (id),
                FOREIGN KEY (area_id) REFERENCES areas (id)
            )
        ''')
        
        # Crear usuario por defecto si no existe
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "folp2024"))
            
        conn.commit()

init_db()

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# Modelos Pydantic para el API
class LoginRequest(BaseModel):
    username: str
    password: str

class TransactionCreate(BaseModel):
    item_id: str
    type: str
    persona_id: str
    area_id: str
    observaciones: Optional[str] = ""

class ItemCreate(BaseModel):
    nombre: str
    codigo_patrimonial: str
    categoria: str
    descripcion: Optional[str] = ""

class PersonaCreate(BaseModel):
    nombre_completo: str
    rol: Optional[str] = ""

class AreaCreate(BaseModel):
    nombre_area: str

# API Endpoints
@app.post("/api/login")
def login(req: LoginRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (req.username, req.password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {"status": "success", "token": "dummy-token-123"} # En un caso real usar JWT
    raise HTTPException(status_code=401, detail="Credenciales incorrectas")

@app.get("/api/init")
def get_all_data():
    conn = get_db()
    cursor = conn.cursor()
    
    data = {}
    
    # Obtener áreas
    cursor.execute("SELECT id, nombre_area FROM areas")
    data["areas"] = [{"id": str(row["id"]), "nombre_area": row["nombre_area"]} for row in cursor.fetchall()]
    
    # Obtener personas
    cursor.execute("SELECT id, nombre_completo, rol FROM personas")
    data["personas"] = [{"id": str(row["id"]), "nombre_completo": row["nombre_completo"], "rol": row["rol"]} for row in cursor.fetchall()]
    
    # Obtener items
    cursor.execute("SELECT id, nombre, codigo_patrimonial, categoria, descripcion FROM items")
    data["items"] = [{"id": str(row["id"]), "nombre": row["nombre"], "codigo_patrimonial": row["codigo_patrimonial"], "categoria": row["categoria"], "descripcion": row["descripcion"]} for row in cursor.fetchall()]
    
    # Obtener transacciones
    cursor.execute("SELECT id, item_id, type, persona_id, area_id, observaciones, timestamp FROM transactions ORDER BY timestamp DESC")
    data["transactions"] = []
    for row in cursor.fetchall():
        data["transactions"].append({
            "id": str(row["id"]),
            "item_id": str(row["item_id"]),
            "type": row["type"],
            "persona_id": str(row["persona_id"]),
            "area_id": str(row["area_id"]),
            "observaciones": row["observaciones"],
            "timestamp": row["timestamp"]
        })
        
    conn.close()
    return data

@app.post("/api/transactions")
def create_transaction(tx: TransactionCreate):
    conn = get_db()
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO transactions (item_id, type, persona_id, area_id, observaciones, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
        (tx.item_id, tx.type, tx.persona_id, tx.area_id, tx.observaciones, timestamp)
    )
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/items")
def create_item(item: ItemCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO items (nombre, codigo_patrimonial, categoria, descripcion) VALUES (?, ?, ?, ?)",
        (item.nombre, item.codigo_patrimonial, item.categoria, item.descripcion)
    )
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/personas")
def create_persona(p: PersonaCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO personas (nombre_completo, rol) VALUES (?, ?)",
        (p.nombre_completo, p.rol)
    )
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/areas")
def create_area(a: AreaCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO areas (nombre_area) VALUES (?)",
        (a.nombre_area,)
    )
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/seed")
def seed_data():
    conn = get_db()
    cursor = conn.cursor()
    
    # Limpiar datos anteriores para simplificar
    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM items")
    cursor.execute("DELETE FROM personas")
    cursor.execute("DELETE FROM areas")
    
    areas = ["Soporte Informática", "Laboratorio de Redes", "Aulas de Computación"]
    personas = [("Bautista Merlo", "Administrador"), ("Juan Perez", "Técnico")]
    items = [("Notebook Dell Vostro", "PAT-1020", "Hardware", "Core i7, 16GB RAM")]
    
    for area in areas:
        cursor.execute("INSERT INTO areas (nombre_area) VALUES (?)", (area,))
        
    for nombre, rol in personas:
        cursor.execute("INSERT INTO personas (nombre_completo, rol) VALUES (?, ?)", (nombre, rol))
        
    for nombre, cod, cat, desc in items:
        cursor.execute("INSERT INTO items (nombre, codigo_patrimonial, categoria, descripcion) VALUES (?, ?, ?, ?)", (nombre, cod, cat, desc))
        
    conn.commit()
    conn.close()
    return {"status": "seeded"}


# Servir archivos estáticos del frontend
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/js", StaticFiles(directory="js"), name="js")
app.mount("/icons", StaticFiles(directory="icons"), name="icons")

@app.get("/manifest.json")
def read_manifest():
    return FileResponse("manifest.json")

@app.get("/sw.js")
def read_sw():
    return FileResponse("sw.js", media_type="application/javascript")

@app.get("/")
def read_index():
    return FileResponse("index.html")

