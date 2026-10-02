from fastapi import APIRouter

from app.api.agent import router as agent_router
from app.api.analyze import router as analyze_router
from app.api.datasets import router as datasets_router
from app.api.health import router as health_router

from app.api.auth import router as auth_router

# V1 Router
v1_router = APIRouter()
v1_router.include_router(health_router)
v1_router.include_router(auth_router)
v1_router.include_router(datasets_router)
v1_router.include_router(agent_router)
v1_router.include_router(analyze_router)

# Main API Router
api_router = APIRouter()

# Include versioned API under /api/v1
api_router.include_router(v1_router, prefix="/api/v1")

# Include unversioned legacy routes for backward compatibility
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(datasets_router)
api_router.include_router(agent_router)
api_router.include_router(analyze_router)