from fastapi import APIRouter, HTTPException
import os
import requests

router = APIRouter(prefix="/monsters", tags=["monsters"])

# Configurações Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

# =========================
# GET MONSTERS
# =========================
@router.get("/")
def get_monsters(
    name: str | None = None,
    weakness: str | None = None,
    min_level: int | None = None
):
    """
    Retorna a lista de monstros.
    Filtros opcionais:
    - name (str): busca parcial no nome (ex: "Dragon")
    - weakness (str): busca parcial em fraquezas (ex: "ice")
    - min_level (int): filtra monstros com level >= valor informado
    """
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
        raise HTTPException(status_code=resp.status_code, detail="Erro ao buscar monstros")

    return resp.json()
