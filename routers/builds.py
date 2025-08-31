from fastapi import APIRouter, HTTPException, Depends
from uuid import uuid4
from core.auth import get_current_user
from core.database import supabase_get, supabase_post, supabase_delete

router = APIRouter(prefix="/builds", tags=["builds"])

# =========================
# CRIAR BUILD
# =========================
@router.post("/")
def create_build(
    items: dict,
    imbuements: dict,
    gems: dict,
    monster_id: int | None = None,
    wheel_of_destiny: dict | None = None,
    total_attributes: dict | None = None,
    current_user: dict = Depends(get_current_user)
):
    build_id = str(uuid4())
    build_data = {
        "id": build_id,
        "user_id": current_user["id"],
        "items": items,
        "imbuements": imbuements,
        "gems": gems,
        "monster_id": monster_id,
        "wheel_of_destiny": wheel_of_destiny,
        "total_attributes": total_attributes,
    }

    resp = supabase_post("builds", build_data)
    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=500, detail="Erro ao criar build")

    return {"msg": "Build criada com sucesso!", "id": build_id}

# =========================
# LISTAR BUILDS DO USUÁRIO
# =========================
@router.get("/")
def list_my_builds(current_user: dict = Depends(get_current_user)):
    resp = supabase_get("builds", {"user_id": f"eq.{current_user['id']}"})
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Erro ao buscar builds")

    return resp.json()

# =========================
# PEGAR BUILD ESPECÍFICA
# =========================
@router.get("/{build_id}")
def get_build(build_id: str, current_user: dict = Depends(get_current_user)):
    resp = supabase_get("builds", {"id": f"eq.{build_id}", "user_id": f"eq.{current_user['id']}"})
    if resp.status_code != 200 or not resp.json():
        raise HTTPException(status_code=404, detail="Build não encontrada")

    return resp.json()[0]

# =========================
# DELETAR BUILD
# =========================
@router.delete("/{build_id}")
def delete_build(build_id: str, current_user: dict = Depends(get_current_user)):
    resp = supabase_delete("builds", f"id=eq.{build_id}&user_id=eq.{current_user['id']}")
    if resp.status_code not in (200, 204):
        raise HTTPException(status_code=500, detail="Erro ao deletar build")

    return {"msg": "Build deletada com sucesso!"}
