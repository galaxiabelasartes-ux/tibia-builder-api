from fastapi import APIRouter, HTTPException
from core.database import supabase_get

router = APIRouter(prefix="/monsters", tags=["monsters"])

@router.get("/")
def get_monsters(
    name: str | None = None,
    weakness: str | None = None,
    min_level: int | None = None
):
    """
    Retorna a lista de monstros com filtros opcionais:
    - name (str): busca parcial no nome (ex: "Dragon")
    - weakness (str): busca parcial em fraquezas (ex: "ice")
    - min_level (int): filtra monstros com level >= valor informado
    """
    params = {}
    if name is not None:
        params["name"] = f"ilike.%{name}%"
    if weakness is not None:
        params["weaknesses"] = f"ilike.%{weakness}%"
    if min_level is not None:
        params["level"] = f"gte.{min_level}"

    resp = supabase_get("monsters", params)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Erro ao buscar monstros")

    return resp.json()
