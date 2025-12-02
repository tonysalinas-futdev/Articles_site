from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL="sqlite+aiosqlite:///./articles.db"

Base=declarative_base()


engine=create_async_engine(DATABASE_URL, future=True)

AsyncLocalSession=sessionmaker(autoflush=False, autocommit=False, bind=engine, class_=AsyncSession)

async def get_session():
    async  with AsyncLocalSession() as session:
        yield session