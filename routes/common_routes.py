from fastapi import APIRouter, Depends,status, Request, HTTPException
from repositorys.sqlalchemy_article_repo import SqlalchemyArticleRepo
from repositorys.sqlalchemy_tag_repo import SqlAlchemyTagRepo
from limiter_config import limiter
import schemas
from services.article_service import publish, coment
from services.tags_service import create_tag
from dependences import  get_repo, get_tag_repo
from typing import Union

router=APIRouter(prefix="/article", tags=["Articles"])


#Ruta para obtener un artículo según su id
@router.get("/get_one/{article_id}", response_model=schemas.SendArticleDetail, status_code=status.HTTP_200_OK)
async def get_article_by_id(article_id:int, service:SqlalchemyArticleRepo=Depends(get_repo)):
    article=await service.get_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="No se ha podido encontrar ese artículo")
    return schemas.SendArticleDetail.model_validate(article)


#Ruta para obtener todos los articulos
@limiter.limit("60/minute")
@router.get("/get_all", response_model=schemas.GetAllPaginated, status_code=status.HTTP_200_OK)
async def get_all_articles(request:Request,cursor:int=0,service:SqlalchemyArticleRepo=Depends(get_repo)):
    articles=await service.get_all(cursor)
    return articles


#Ruta para obtener todos los artículos según los filtros
@limiter.limit("60/minute")
@router.post("/filter", response_model=schemas.GetAllPaginated, status_code=status.HTTP_200_OK)
async def search_articles(request:Request,model:schemas.SearchByFilters, cursor:int=0,service:SqlalchemyArticleRepo=Depends(get_repo)):
    articles=await service.search_by_filters(model,cursor)
    return articles

