from fastapi import FastAPI
from pydantic import BaseModel
import asyncpg
import os
import json

app = FastAPI()

# Modelo que valida a entrada do usuário
class Monster(BaseModel):
    name: str
    hp: int
    level: int
    attributes: dict

@app.post("/monsters")
async def create_monster(monster: Monster):
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
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
        json.dumps(monster.attributes)  # garante formato JSON
    )
    await conn.close()
    return dict(row)
    
@app.get("/")
async def root():
    return {"message": "Tibia Builder API Online!"}
