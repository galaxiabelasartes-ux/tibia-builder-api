from fastapi import APIRouter, HTTPException
from core.database import supabase_get

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/")
def get_items(
    slot: int | None = None,
    vocation: str | None = None,
    min_level: int | None = None
):
    """
    Retorna a lista de itens com filtros opcionais:
    - slot (int): filtra por slot (1=head, 2=armor, etc.)
    - vocation (str): Knight, Paladin, Druid, Sorcerer
    - min_level (int): nível mínimo requerido
    """
    params = {}
    if slot is not None:
        params["slot"] = f"eq.{slot}"
    if vocation is not None:
        params["vocation"] = f"ilike.%{vocation}%"
    if min_level is not None:
        params["level_required"] = f"gte.{min_level}"

    resp = supabase_get("items", params)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Erro ao buscar itens")

    return resp.json()
