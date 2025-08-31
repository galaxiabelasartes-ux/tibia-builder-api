from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import requests
import os

app = FastAPI(
    title="Tibia Builder API",
    description="Backend para o projeto Tibia Set Builder",
    version="1.0.0"
)

#Configurações Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

# Configurações JWT
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Funções auxiliares
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# =========================
# REGISTER
# =========================
@app.post("/register")
def register(username: str, email: str, password: str):
    hashed_pw = get_password_hash(password)
    user = {"username": username, "email": email, "password_hash": hashed_pw}

    resp = requests.post(f"{SUPABASE_URL}/rest/v1/user", headers={**headers, "Content-Type": "application/json"}, json=user)
    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return {"msg": "Usuário registrado com sucesso!"}

# =========================
# LOGIN
# =========================
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Busca usuário pelo email
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/user?email=eq.{form_data.username}",
        headers=headers
    )
    if resp.status_code != 200 or not resp.json():
        raise HTTPException(status_code=400, detail="Usuário não encontrado")

    user = resp.json()[0]
    if not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Senha incorreta")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data={"sub": user["email"]}, expires_delta=access_token_expires)

    return {"access_token": token, "token_type": "bearer"}

@app.get("/")
def root():
    return {"message": "Tibia Builder API Online!"}

# =========================
# ITEMS
# =========================
@app.get("/items")
def get_items(
    slot: int | None = None,
    vocation: str | None = None,
    min_level: int | None = None
):
    url = f"{SUPABASE_URL}/rest/v1/items"
    params = {}
    if slot is not None:
        params["slot"] = f"eq.{slot}"
    if vocation is not None:
        # suporta múltiplas vocações (Knight, Paladin, Druid, Sorcerer)
        params["vocation"] = f"ilike.%{vocation}%"
    if min_level is not None:
        params["level_required"] = f"gte.{min_level}"

    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()

# =========================
# MONSTERS
# =========================
@app.get("/monsters")
def get_monsters(
    name: str | None = None,
    weakness: str | None = None,
    min_level: int | None = None
):
    url = f"{SUPABASE_URL}/rest/v1/monsters"
    params = {}
    if name is not None:
        params["name"] = f"ilike.%{name}%"
    if weakness is not None:
        params["weaknesses"] = f"ilike.%{weakness}%"
    if min_level is not None:
        params["level"] = f"gte.{min_level}"

    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()

# =========================
# IMBUEMENTS
# =========================
@app.get("/imbuements")
def get_imbuements(
    applicable_slot: str | None = None,
    min_bonus_attack: int | None = None,
    min_bonus_defense: int | None = None,
    min_bonus_magic: int | None = None
):
    url = f"{SUPABASE_URL}/rest/v1/imbuements"
    params = {}
    if applicable_slot is not None:
        params["applicable_slots"] = f"ilike.%{applicable_slot}%"
    if min_bonus_attack is not None:
        params["bonus_attack"] = f"gte.{min_bonus_attack}"
    if min_bonus_defense is not None:
        params["bonus_defense"] = f"gte.{min_bonus_defense}"
    if min_bonus_magic is not None:
        params["bonus_magic"] = f"gte.{min_bonus_magic}"

    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()

# =========================
# GEMS
# =========================
@app.get("/gems")
def get_gems(
    min_bonus_attack: int | None = None,
    min_bonus_defense: int | None = None,
    min_bonus_magic: int | None = None
):
    url = f"{SUPABASE_URL}/rest/v1/gems"
    params = {}
    if min_bonus_attack is not None:
        params["bonus_attack"] = f"gte.{min_bonus_attack}"
    if min_bonus_defense is not None:
        params["bonus_defense"] = f"gte.{min_bonus_defense}"
    if min_bonus_magic is not None:
        params["bonus_magic"] = f"gte.{min_bonus_magic}"

    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()
