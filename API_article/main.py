from fastapi import FastAPI
from routes import router
from database.database import engine
import database.models as models
from contextlib import asynccontextmanager
from slowapi import  _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from limiter_config import limiter
from slowapi.middleware import SlowAPIMiddleware


@asynccontextmanager
async def lifespan(app:FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield





app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.state.limiter=limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)