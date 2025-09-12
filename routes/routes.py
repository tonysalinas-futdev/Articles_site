from fastapi import APIRouter, Depends,status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_session
from repositorys.sqlalchemy_article_repo import SqlalchemyArticleRepo
from repositorys.sqlalchemy_tag_repo import SqlAlchemyTagRepo
from limiter_config import limiter
import schemas
from typing import List
from services.article_service import publish
from services.tags_service import create_tag
router=APIRouter(prefix="/article", tags=["Articles"])


async def get_db(db:AsyncSession=Depends(get_session)):
    return db

async def get_repo(session:AsyncSession=Depends(get_db)):
    return SqlalchemyArticleRepo(session)


async def get_tag_repo(session:AsyncSession=Depends(get_db)):
    return SqlAlchemyTagRepo(session)



#Ruta para obtener un artículo según su id
@router.get("/get_one/{article_id}", response_model=schemas.SendArticleDetail, status_code=status.HTTP_200_OK)
async def get_article_by_id(article_id:int, service:SqlalchemyArticleRepo=Depends(get_repo)):
    article=await service.get_by_id(article_id)
    return article


#Ruta para obtener todos los articulos
@router.get("/get_all", response_model=schemas.GetAllPaginated, status_code=status.HTTP_200_OK)
async def get_all_articles(cursor:int=0,service:SqlalchemyArticleRepo=Depends(get_repo)):
    articles=await service.get_all(cursor)
    return articles


#Ruta para crear un artículo
@router.post("/create", response_model=schemas.MsgResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("12/minute")
async def create(request:Request,model:schemas.CreateArticle, repo:SqlalchemyArticleRepo=Depends(get_repo), tag_repo:SqlAlchemyTagRepo=Depends(get_tag_repo)):
    await publish(model,repo,tag_repo)
    
    return {"message":"Artículo creado exitosamente"}




#Ruta para obtener todos los artículos según los filtros
@router.post("/filter", response_model=schemas.GetAllPaginated, status_code=status.HTTP_200_OK)
async def search_articles(model:schemas.SearchByFilters, cursor:int=0,service:SqlalchemyArticleRepo=Depends(get_repo)):
    articles=await service.search_by_filters(model,cursor)
    return articles


#Ruta para obtener todos los artículos según los filtros
@router.post("/create_tag", response_model=schemas.MsgResponse, status_code=status.HTTP_201_CREATED)
async def create_tags(model:schemas.CreateTag,service:SqlAlchemyTagRepo=Depends(get_tag_repo)):
    await create_tag(model, service)
    return {"message":"Tag creado exitosamente"}


