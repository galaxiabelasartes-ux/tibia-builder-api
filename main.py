from fastapi import FastAPI
from pydantic import BaseModel
import asyncpg
import os

app = FastAPI()

# Modelo para validar entrada
class Creature(BaseModel):
    name: str
    hp: int
    level: int
    attributes: dict

@app.post("/creatures")
async def create_creature(creature: Creature):
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    query = """
        INSERT INTO monsters (name, hp, level, attributes)
        VALUES ($1, $2, $3, $4)
        RETURNING id, name, hp, level, attributes;
    """
    row = await conn.fetchrow(query, creature.name, creature.hp, creature.level, creature.attributes)
    await conn.close()
    return dict(row)
