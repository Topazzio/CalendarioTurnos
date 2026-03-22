"""
admin.py  –  Rutas de administración para Doble AA
Requiere: pip install python-jose[cryptography] bcrypt
"""

import os
import sqlite3
import bcrypt
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────

SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", "68b88e51901c2d4d10172ab973a408bb61765e0d50d597367701e1efbdcdf6da")
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8   # 8 horas

ADMIN_USER = os.getenv("ADMIN_USER", "admin")

# ADMIN_HASH debe ser el hash bcrypt de tu contraseña, generado con:
# python -c "import bcrypt; print(bcrypt.hashpw('tuPassword'.encode(), bcrypt.gensalt()).decode())"
ADMIN_HASH = os.getenv("ADMIN_HASH", "")

oauth2 = OAuth2PasswordBearer(tokenUrl="/admin/token")
router = APIRouter(prefix="/admin", tags=["admin"])

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ─────────────────────────────────────────────
#  BASE DE DATOS – accesorios.db
# ─────────────────────────────────────────────

DB_PATH = Path(__file__).parent.parent / "accesorios.db"

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS accesorios (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre     TEXT    NOT NULL,
            precio     INTEGER NOT NULL,
            stock      INTEGER NOT NULL DEFAULT 0,
            imagen     TEXT    DEFAULT '',
            categoria  TEXT    DEFAULT 'general',
            activo     INTEGER DEFAULT 1,
            creado_en  TEXT    DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS turnos_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id    TEXT,
            nombre      TEXT,
            telefono    TEXT,
            auto        TEXT,
            anio        TEXT,
            material    TEXT,
            pago        TEXT,
            start_time  TEXT,
            creado_en   TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()

init_db()


# ─────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str

def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2)):
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user: str = payload.get("sub")
        if user is None:
            raise cred_exc
    except JWTError:
        raise cred_exc
    return user

@router.post("/token", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends()):
    if form.username != ADMIN_USER or not verify_password(form.password, ADMIN_HASH):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_token({"sub": form.username})
    return {"access_token": token, "token_type": "bearer"}


# ─────────────────────────────────────────────
#  MODELOS
# ─────────────────────────────────────────────

class AccesorioIn(BaseModel):
    nombre:    str
    precio:    int
    stock:     int
    imagen:    Optional[str] = ""
    categoria: Optional[str] = "general"
    activo:    Optional[int] = 1

class StockUpdate(BaseModel):
    stock: int

class TurnoLog(BaseModel):
    event_id:   str
    nombre:     str
    telefono:   str
    auto:       str
    anio:       str
    material:   str
    pago:       str
    start_time: str


# ─────────────────────────────────────────────
#  ACCESORIOS CRUD
# ─────────────────────────────────────────────

@router.get("/accesorios")
def listar_accesorios(_: str = Depends(verify_token)):
    conn = get_db()
    rows = conn.execute("SELECT * FROM accesorios ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.post("/accesorios", status_code=201)
def crear_accesorio(data: AccesorioIn, _: str = Depends(verify_token)):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO accesorios (nombre,precio,stock,imagen,categoria,activo) VALUES (?,?,?,?,?,?)",
        (data.nombre, data.precio, data.stock, data.imagen, data.categoria, data.activo)
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return {"id": new_id, "message": "Accesorio creado"}

@router.put("/accesorios/{acc_id}")
def actualizar_accesorio(acc_id: int, data: AccesorioIn, _: str = Depends(verify_token)):
    conn = get_db()
    conn.execute(
        "UPDATE accesorios SET nombre=?,precio=?,stock=?,imagen=?,categoria=?,activo=? WHERE id=?",
        (data.nombre, data.precio, data.stock, data.imagen, data.categoria, data.activo, acc_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Actualizado"}

@router.patch("/accesorios/{acc_id}/stock")
def actualizar_stock(acc_id: int, data: StockUpdate, _: str = Depends(verify_token)):
    conn = get_db()
    conn.execute("UPDATE accesorios SET stock=? WHERE id=?", (data.stock, acc_id))
    conn.commit()
    conn.close()
    return {"message": "Stock actualizado"}

@router.delete("/accesorios/{acc_id}")
def eliminar_accesorio(acc_id: int, _: str = Depends(verify_token)):
    conn = get_db()
    conn.execute("DELETE FROM accesorios WHERE id=?", (acc_id,))
    conn.commit()
    conn.close()
    return {"message": "Eliminado"}


# ─────────────────────────────────────────────
#  TURNOS LOG
# ─────────────────────────────────────────────

@router.post("/turnos")
def registrar_turno(data: TurnoLog):
    """Llamado internamente desde /book para persistir cada turno confirmado."""
    conn = get_db()
    conn.execute(
        "INSERT INTO turnos_log (event_id,nombre,telefono,auto,anio,material,pago,start_time) VALUES (?,?,?,?,?,?,?,?)",
        (data.event_id, data.nombre, data.telefono, data.auto, data.anio, data.material, data.pago, data.start_time)
    )
    conn.commit()
    conn.close()

@router.get("/turnos")
def ver_turnos(_: str = Depends(verify_token)):
    conn = get_db()
    rows = conn.execute("SELECT * FROM turnos_log ORDER BY start_time DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/stats")
def stats(_: str = Depends(verify_token)):
    conn = get_db()

    # turnos por material
    mat = conn.execute(
        "SELECT material, COUNT(*) as total FROM turnos_log GROUP BY material ORDER BY total DESC"
    ).fetchall()

    # turnos por mes
    mes = conn.execute(
        "SELECT strftime('%Y-%m', start_time) as mes, COUNT(*) as total FROM turnos_log GROUP BY mes ORDER BY mes DESC LIMIT 6"
    ).fetchall()

    # accesorios con bajo stock
    bajo = conn.execute(
        "SELECT id, nombre, stock FROM accesorios WHERE stock <= 3 AND activo=1 ORDER BY stock ASC"
    ).fetchall()

    total_turnos = conn.execute("SELECT COUNT(*) FROM turnos_log").fetchone()[0]
    total_acc    = conn.execute("SELECT COUNT(*) FROM accesorios WHERE activo=1").fetchone()[0]

    conn.close()
    return {
        "total_turnos":    total_turnos,
        "total_accesorios": total_acc,
        "por_material":    [dict(r) for r in mat],
        "por_mes":         [dict(r) for r in mes],
        "bajo_stock":      [dict(r) for r in bajo],
    }