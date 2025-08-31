from fastapi import APIRouter, HTTPException
import os
import requests

router = APIRouter(prefix="/items", tags=["items"])

# Configurações Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

# =========================
# GET ITEMS
# =========================
@router.get("/")
def get_items(
    slot: int | None = None,
    vocation: str | None = None,
    min_level: int | None = None
):
    """
    Retorna a lista de itens.
    Filtros opcionais:
    - slot (int): filtra por slot (1 = head, 2 = armor, etc.)
    - vocation (str): filtra por vocação (Knight, Paladin, Druid, Sorcerer)
    - min_level (int): nível mínimo requerido
    """
    url = f"{SUPABASE_URL}/rest/v1/items"
    params = {}

    if slot is not None:
        params["slot"] = f"eq.{slot}"
    if vocation is not None:
        params["vocation"] = f"ilike.%{vocation}%"
    if min_level is not None:
        params["level_required"] = f"gte.{min_level}"

    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Erro ao buscar itens")

    return resp.json()
