from fastapi import FastAPI, Request,HTTPException
from app.routes.common_routes import router
from app.routes.admin_routes import router_admin
from app.routes.writers_routes import router_writers
from app.routes.users_routes import router_users
from app.database.database import engine
import app.database.models as models
from contextlib import asynccontextmanager
from slowapi import  _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.limiter_config import limiter
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
import asyncio


@asynccontextmanager
async def lifespan(app:FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield




app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.include_router(router_admin)
app.include_router(router_writers)
app.include_router(router_users)

@app.get("/")
async def get_welcome():
    return {
        "Saludo":"Holaaa",
        "Detalles":"API para sitio de artículos",
        "Código e instrucciones":"https://github.com/tonysalinas-futdev/Articles_site",
        "Mi correo":"kroosismo0202@gmail.com (kroos enjoyer, si)",
        "Ver todos los endpoints":"https://articles-site-1.onrender.com/docs"
    }


app.state.limiter=limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

origins = [
    "http://127.0.0.1:4200",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",

]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            
    allow_credentials=True,           
    allow_methods=["*"],              
    allow_headers=["*"],             
)


#Middleware para timeout
@app.middleware("http")
async def timeout(request:Request, call_next):
    try:
        return await asyncio.wait_for(call_next(request), timeout=60)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="El tiempo de espera se ha agotado")
    
