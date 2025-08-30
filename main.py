from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import asyncpg
import os
import ssl
from typing import Optional, Dict

app = FastAPI(title="Tibia Builder API")

# Modelo de entrada
class Monster(BaseModel):
    name: str
    hp: int
    level: int
    attributes: Dict[str, str | int]

# Autenticação simples via token de API
def verify_token(authorization: Optional[str] = Header(None)):
    API_TOKEN = os.getenv("API_TOKEN")  # Defina no Render
    if not API_TOKEN:
        raise HTTPException(status_code=500, detail="API_TOKEN não configurado no servidor")
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=403, detail="Acesso negado: token inválido ou ausente")

@app.post("/monsters")
async def create_monster(monster: Monster, auth: None = Depends(verify_token)):
    try:
        # Conexão segura com SSL
        ssl_context = ssl.create_default_context()
        conn = await asyncpg.connect(
            os.getenv("DATABASE_URL"),
            ssl=ssl_context
        )

        query = """
            INSERT INTO monsters (name, hp, level, attributes)
            VALUES ($1, $2, $3, $4)
            RETURNING id, name, hp, level, attributes;
        """

        row = await conn.fetchrow(
            query,
            monster.name,
            monster.hp,
            monster.level,
            monster.attributes
        )

        await conn.close()

        return {
            "message": "Monstro criado com sucesso!",
            "data": dict(row)
        }

    except asyncpg.PostgresError as e:
        raise HTTPException(status_code=400, detail=f"Erro no banco: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Tibia Builder API Online e Segura!"}
