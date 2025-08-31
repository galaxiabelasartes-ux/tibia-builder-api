from fastapi import APIRouter, HTTPException
from core.database import supabase_get

router = APIRouter(prefix="/imbuements", tags=["imbuements"])

@router.get("/")
def get_imbuements(
    applicable_slot: str | None = None,
    min_bonus_attack: int | None = None,
    min_bonus_defense: int | None = None,
    min_bonus_magic: int | None = None
):
    """
    Retorna a lista de imbuements com filtros opcionais:
    - applicable_slot (str): busca parcial nos slots aplicáveis (ex: "weapon")
    - min_bonus_attack (int): bônus de ataque mínimo
    - min_bonus_defense (int): bônus de defesa mínimo
    - min_bonus_magic (int): bônus de magia mínimo
    """
    params = {}
    if applicable_slot is not None:
        params["applicable_slots"] = f"ilike.%{applicable_slot}%"
    if min_bonus_attack is not None:
        params["bonus_attack"] = f"gte.{min_bonus_attack}"
    if min_bonus_defense is not None:
        params["bonus_defense"] = f"gte.{min_bonus_defense}"
    if min_bonus_magic is not None:
        params["bonus_magic"] = f"gte.{min_bonus_magic}"

    resp = supabase_get("imbuements", params)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Erro ao buscar imbuements")

    return resp.json()
