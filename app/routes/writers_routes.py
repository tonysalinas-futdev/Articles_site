from fastapi import APIRouter, Depends,status, Request,HTTPException
from app.repositorys.sqlalchemy_article_repo import SqlalchemyArticleRepo
from app.repositorys.sqlalchemy_tag_repo import SqlAlchemyTagRepo
from app.limiter_config import limiter
import app.schemas as schemas
from app.services.article_service import publish, delete
from app.dependences import  get_repo, get_tag_repo
from app.jwt_utils import get_current_user
from typing import Union

router_writers=APIRouter(prefix="/writers", tags=["Articles"])


#Ruta para crear un artículo
@router_writers.post("/create", response_model=schemas.MsgResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("12/minute")
async def create(request:Request,model:schemas.CreateArticle, repo:SqlalchemyArticleRepo=Depends(get_repo), tag_repo:SqlAlchemyTagRepo=Depends(get_tag_repo), data=Depends(get_current_user)):
    if data.get("role")!="writer" and data.get("role")!="admin":
        raise HTTPException(status_code=401, detail="Usted no tiene acceso a esta ruta")
    await publish(data.get("id"),model,repo,tag_repo)
    
    return {"message":"Artículo creado exitosamente"}

#Ruta para que un escritor elimine cualquiera de sus artículos
@router_writers.delete("/delete_article", response_model=schemas.MsgResponse, status_code=status.HTTP_200_OK)
async def delete_article(article_id:int,repo:SqlalchemyArticleRepo=Depends(get_repo),data=Depends(get_current_user)):

    if data.get("role")!="writer":
        raise HTTPException(status_code=401, detail="Usted no está autorizado para acceder a esta ruta")
    
    article=await repo.get_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="No se pudo encontrar el artículo")
    if article.autor_id!=data.get("id"):
        raise HTTPException(status_code=401, detail="Usted no está autorizado para acceder a esta ruta")
    
    await repo.delete(article)
    
    return {"message":"Artículo eliminado exitosamente"}
