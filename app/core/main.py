from fastapi import FastAPI
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.interfaces.v1.api.routes.scripts import router as scripts_router
from app.interfaces.v1.api.routes.generated_scripts import router as geberated_script_router
from app.interfaces.v1.api.dependencies.rate_limit import limiter





app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

app.include_router(scripts_router)
app.include_router(geberated_script_router)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"},
    )

@app.get("/")
async def read_root():  
    return {"Hello": "World"}