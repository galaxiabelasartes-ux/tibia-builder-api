from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

# Importando helpers do core
from core.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from core.database import supabase_get, supabase_post, supabase_patch, supabase_delete

router = APIRouter(prefix="/users", tags=["users"])

# =========================
# REGISTER
# =========================
@router.post("/register")
def register(username: str, email: str, password: str):
    # Verifica se email já existe
    resp_check = supabase_get("users", {"email": f"eq.{email}"})
    if resp_check.status_code == 200 and resp_check.json():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    hashed_pw = get_password_hash(password)
    user = {"username": username, "email": email, "password_hash": hashed_pw}

    resp = supabase_post("users", user)
    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=500, detail="Erro ao registrar usuário")

    return {"msg": "Usuário registrado com sucesso!"}

# =========================
# LOGIN
# =========================
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    resp = supabase_get("users", {"email": f"eq.{form_data.username}"})
    if resp.status_code != 200 or not resp.json():
        raise HTTPException(status_code=400, detail="Usuário não encontrado")

    user = resp.json()[0]
    if not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Senha incorreta")

    token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": token, "token_type": "bearer"}

# =========================
# ME (GET)
# =========================
@router.get("/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    safe_user = {k: v for k, v in current_user.items() if k != "password_hash"}
    return {"user": safe_user}

# =========================
# UPDATE USER (PATCH)
# =========================
@router.patch("/me")
def update_user_me(
    username: str | None = None,
    email: str | None = None,
    password: str | None = None,
    current_user: dict = Depends(get_current_user)
):
    update_data = {}
    if username:
        update_data["username"] = username
    if email:
        update_data["email"] = email
    if password:
        update_data["password_hash"] = get_password_hash(password)

    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

    resp = supabase_patch("users", f"id=eq.{current_user['id']}", update_data)
    if resp.status_code not in (200, 204):
        raise HTTPException(status_code=500, detail="Erro ao atualizar usuário")

    return {"msg": "Usuário atualizado com sucesso!"}

# =========================
# DELETE USER
# =========================
@router.delete("/me")
def delete_user_me(current_user: dict = Depends(get_current_user)):
    resp = supabase_delete("users", f"id=eq.{current_user['id']}")
    if resp.status_code not in (200, 204):
        raise HTTPException(status_code=500, detail="Erro ao deletar usuário")

    return {"msg": "Usuário deletado com sucesso!"}
