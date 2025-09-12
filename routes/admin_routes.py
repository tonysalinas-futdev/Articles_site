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

router_admin=APIRouter(prefix="/admin", tags=["Admin"])


async def get_db(db:AsyncSession=Depends(get_session)):
    return db

async def get_repo(session:AsyncSession=Depends(get_db)):
    return SqlalchemyArticleRepo(session)


async def get_tag_repo(session:AsyncSession=Depends(get_db)):
    return SqlAlchemyTagRepo(session)


@router_admin.post("/create_tag", response_model=schemas.TagBase, status_code=status.HTTP_200_OK)
async def create(model:schemas.CreateTag,repo:SqlAlchemyTagRepo=Depends(get_tag_repo)):
    return await create_tag(model,repo)
    