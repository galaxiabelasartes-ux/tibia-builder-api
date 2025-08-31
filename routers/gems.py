from fastapi import APIRouter, HTTPException
from core.database import supabase_get

router = APIRouter(prefix="/gems", tags=["gems"])

@router.get("/")
def get_gems(
    min_bonus_attack: int | None = None,
    min_bonus_defense: int | None = None,
    min_bonus_magic: int | None = None
):
    """
    Retorna a lista de gemas com filtros opcionais:
    - min_bonus_attack (int): bônus de ataque mínimo
    - min_bonus_defense (int): bônus de defesa mínimo
    - min_bonus_magic (int): bônus de magia mínimo
    """
    params = {}
    if min_bonus_attack is not None:
        params["bonus_attack"] = f"gte.{min_bonus_attack}"
    if min_bonus_defense is not None:
        params["bonus_defense"] = f"gte.{min_bonus_defense}"
    if min_bonus_magic is not None:
        params["bonus_magic"] = f"gte.{min_bonus_magic}"

    resp = supabase_get("gems", params)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Erro ao buscar gemas")

    return resp.json()
