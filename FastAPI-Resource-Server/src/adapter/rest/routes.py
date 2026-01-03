from fastapi import APIRouter

health_routers = APIRouter()

crud_routers = APIRouter()

@health_routers.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}