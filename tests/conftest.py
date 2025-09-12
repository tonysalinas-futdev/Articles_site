import pytest
import pytest_asyncio
from database.models import Article, Tags
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from repositorys.sqlalchemy_article_repo import SqlalchemyArticleRepo
from repositorys.sqlalchemy_tag_repo import SqlAlchemyTagRepo
from database.database import Base
from faker import Faker
import random

DATABASE_URL="sqlite+aiosqlite:///:memory:"
engine=create_async_engine(DATABASE_URL, echo=True, future=True)


AsyncLocalSession=sessionmaker(engine, autoflush=False,class_=AsyncSession)

@pytest_asyncio.fixture
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@pytest_asyncio.fixture
async def get_session(create_db):
    async with AsyncLocalSession() as session:
        yield session

@pytest_asyncio.fixture
async def get_article_repo(get_session):
    return SqlalchemyArticleRepo(get_session)

@pytest_asyncio.fixture
async def get_tag_repo(get_session):
    return SqlAlchemyTagRepo(get_session)

@pytest_asyncio.fixture
async def data_in_bd(get_session,get_tag_repo):
    fake=Faker()
    tags=["#python", "#java", "#programacion", "#software", "#go", "#fastapi", "#laravel","#django"]
    tags_add=[Tags(name=tag) for tag in tags]
    get_session.add_all(tags_add)
    await get_session.flush()

    for i in range (15):
        article=Article(
            title=fake.sentence(),
            content=fake.text(),
            autor_id=random.randint(1,100)


        )
        
        article_tags=random.sample(tags_add, random.randint(1, len(tags)-1))
        article.tags.extend(article_tags)
        get_session.add(article)


    await get_session.commit()
