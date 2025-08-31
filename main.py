from fastapi import FastAPI, HTTPException
import requests
import os

app = FastAPI()

# Configurações do Supabase (usamos anon key para leitura)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

@app.get("/")
def root():
    return {"message": "Tibia Builder API Online!"}

@app.get("/items")
def get_items():
    resp = requests.get(f"{SUPABASE_URL}/rest/v1/items", headers=headers)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()

@app.get("/monsters")
def get_monsters():
    resp = requests.get(f"{SUPABASE_URL}/rest/v1/monsters", headers=headers)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()

@app.get("/imbuements")
def get_imbuements():
    resp = requests.get(f"{SUPABASE_URL}/rest/v1/imbuements", headers=headers)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()

@app.get("/gems")
def get_gems():
    resp = requests.get(f"{SUPABASE_URL}/rest/v1/gems", headers=headers)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()
