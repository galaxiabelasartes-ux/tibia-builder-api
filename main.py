from fastapi import FastAPI, status, HTTPException, Depends
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

# Configurações Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

# Configurações JWT
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# =========================
# Funções auxiliares
# =========================
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
    # Verifica se email já existe
    resp_check = requests.get(f"{SUPABASE_URL}/rest/v1/users?email=eq.{email}", headers=headers)
    if resp_check.status_code == 200 and resp_check.json():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    hashed_pw = get_password_hash(password)
    user = {"username": username, "email": email, "password_hash": hashed_pw}

    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/users",
        headers={**headers, "Content-Type": "application/json"},
        json=user
    )
    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=500, detail="Erro ao registrar usuário")
    return {"msg": "Usuário registrado com sucesso!"}

# =========================
# LOGIN
# =========================
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/users?email=eq.{form_data.username}",
        headers=headers
    )
    if resp.status_code != 200 or not resp.json():
        raise HTTPException(status_code=400, detail="Usuário não encontrado")

    user = resp.json()[0]
    if not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Senha incorreta")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=access_token_expires
    )

    return {"access_token": token, "token_type": "bearer"}

# =========================
# FUNÇÃO AUXILIAR GET USER
# =========================
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/users?email=eq.{email}",
        headers=headers
    )
    if resp.status_code != 200 or not resp.json():
        raise credentials_exception

    return resp.json()[0]

# =========================
# ENDPOINT PROTEGIDO
# =========================
@app.get("/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    # Esconde o hash da senha na resposta
    safe_user = {k: v for k, v in current_user.items() if k != "password_hash"}
    return {"user": safe_user}

# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {"message": "Tibia Builder API Online!"}
