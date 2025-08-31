from fastapi import FastAPI
from routers import users, items, monsters, gems, imbuements, builds

app = FastAPI(
    title="Tibia Builder API",
    description="Backend para o projeto Tibia Set Builder",
    version="1.0.0"
)

# Inclui os routers (cada um em seu arquivo)
app.include_router(users.router)
app.include_router(items.router)
app.include_router(monsters.router)
app.include_router(gems.router)
app.include_router(imbuements.router)
app.include_router(builds.router)

# Rota raiz
@app.get("/")
def root():
    return {"message": "Tibia Builder API Online!"}
