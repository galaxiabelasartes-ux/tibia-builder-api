from fastapi import FastAPI, HTTPException
import requests
import os

app = FastAPI(
    title="Tibia Builder API",
    description="Backend para o projeto Tibia Set Builder",
    version="1.0.0"
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

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
