from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_session
from fastapi import  Depends
from app.repositorys.sqlalchemy_article_repo import SqlalchemyArticleRepo
from app.repositorys.sqlalchemy_tag_repo import SqlAlchemyTagRepo
from app.repositorys.sqlalchemycrud import SqlAlchemyUserRepo



async def get_db(db:AsyncSession=Depends(get_session)):
    return db

async def get_repo(session:AsyncSession=Depends(get_db)):
    return SqlalchemyArticleRepo(session)


async def get_tag_repo(session:AsyncSession=Depends(get_db)):
    return SqlAlchemyTagRepo(session)

async def get_users_repo(session:AsyncSession=Depends(get_db)):
    return SqlAlchemyUserRepo(session)