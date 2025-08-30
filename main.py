from fastapi import FastAPI, HTTPException, Depends, Header, Query
from pydantic import BaseModel
import asyncpg
import os
import ssl
from typing import Optional, Dict, List

app = FastAPI(title="Tibia Builder API")

# Modelo de entrada
class Monster(BaseModel):
    name: str
    hp: int
    level: int
    attributes: Dict[str, str | int]

# Modelo de saída
class MonsterOut(Monster):
    id: int

# Autenticação via token
def verify_token(authorization: Optional[str] = Header(None)):
    API_TOKEN = os.getenv("API_TOKEN")
    if not API_TOKEN:
        raise HTTPException(status_code=500, detail="API_TOKEN não configurado no servidor")
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=403, detail="Acesso negado: token inválido ou ausente")

# POST - Criar monstro
@app.post("/monsters", response_model=MonsterOut)
async def create_monster(monster: Monster, auth: None = Depends(verify_token)):
    try:
        ssl_context = ssl.create_default_context()
        conn = await asyncpg.connect(
            os.getenv("DATABASE_URL"),
            ssl=ssl_context
        )
        await conn.execute("SET my.api_token = $1", os.getenv("API_TOKEN"))

        query = """
            INSERT INTO monsters (name, hp, level, attributes)
            VALUES ($1, $2, $3, $4)
            RETURNING id, name, hp, level, attributes;
        """
        row = await conn.fetchrow(query, monster.name, monster.hp, monster.level, monster.attributes)
        await conn.close()
        return dict(row)

    except asyncpg.PostgresError as e:
        raise HTTPException(status_code=400, detail=f"Erro no banco: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# GET - Listar monstros com filtros
@app.get("/monsters", response_model=List[MonsterOut])
async def list_monsters(
    auth: None = Depends(verify_token),
    name: Optional[str] = Query(None, description="Filtrar por nome"),
    min_level: Optional[int] = Query(None, description="Level mínimo"),
    max_level: Optional[int] = Query(None, description="Level máximo"),
    element: Optional[str] = Query(None, description="Filtrar por elemento")
):
    try:
        ssl_context = ssl.create_default_context()
        conn = await asyncpg.connect(
            os.getenv("DATABASE_URL"),
            ssl=ssl_context
        )
        await conn.execute("SET my.api_token = $1", os.getenv("API_TOKEN"))

        query = "SELECT id, name, hp, level, attributes FROM monsters WHERE 1=1"
        params = []

        if name:
            params.append(f"%{name}%")
            query += f" AND name ILIKE ${len(params)}"
        if min_level is not None:
            params.append(min_level)
            query += f" AND level >= ${len(params)}"
        if max_level is not None:
            params.append(max_level)
            query += f" AND level <= ${len(params)}"
        if element:
            params.append(element)
            query += f" AND attributes->>'element' = ${len(params)}"

        rows = await conn.fetch(query, *params)
        await conn.close()
        return [dict(row) for row in rows]

    except asyncpg.PostgresError as e:
        raise HTTPException(status_code=400, detail=f"Erro no banco: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# PUT - Atualizar monstro
@app.put("/monsters/{monster_id}", response_model=MonsterOut)
async def update_monster(monster_id: int, monster: Monster, auth: None = Depends(verify_token)):
    try:
        ssl_context = ssl.create_default_context()
        conn = await asyncpg.connect(
            os.getenv("DATABASE_URL"),
            ssl=ssl_context
        )
        await conn.execute("SET my.api_token = $1", os.getenv("API_TOKEN"))

        query = """
            UPDATE monsters
            SET name = $1, hp = $2, level = $3, attributes = $4
            WHERE id = $5
            RETURNING id, name, hp, level, attributes;
        """
        row = await conn.fetchrow(query, monster.name, monster.hp, monster.level, monster.attributes, monster_id)
        await conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Monstro não encontrado")
        return dict(row)

    except asyncpg.PostgresError as e:
        raise HTTPException(status_code=400, detail=f"Erro no banco: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# DELETE - Remover monstro
@app.delete("/monsters/{monster_id}")
async def delete_monster(monster_id: int, auth: None = Depends(verify_token)):
    try:
        ssl_context = ssl.create_default_context()
        conn = await asyncpg.connect(
            os.getenv("DATABASE_URL"),
            ssl=ssl_context
        )
        await conn.execute("SET my.api_token = $1", os.getenv("API_TOKEN"))

        query = "DELETE FROM monsters WHERE id = $1 RETURNING id;"
        row = await conn.fetchrow(query, monster_id)
        await conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Monstro não encontrado")
        return {"message": f"Monstro {monster_id} removido com sucesso"}

    except asyncpg.PostgresError as e:
        raise HTTPException(status_code=400, detail=f"Erro no banco: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# Rota raiz
@app.get("/")
async def root():
    return {"message": "Tibia Builder API Online e Segura!"}
