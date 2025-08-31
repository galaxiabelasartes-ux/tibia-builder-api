from fastapi import FastAPI
from routers import users

app = FastAPI(
    title="Tibia Builder API",
    description="Backend para o projeto Tibia Set Builder",
    version="1.0.0"
)

# Inclui apenas os módulos
app.include_router(users.router)
app.include_route(items.router)

@app.get("/")
def root():
    return {"message": "Tibia Builder API Online!"}
