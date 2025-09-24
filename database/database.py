from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
load_dotenv()

Base=declarative_base()


engine=create_async_engine(url=os.getenv("DATABASE_URL"), future=True)

AsyncLocalSession=sessionmaker(autoflush=False, autocommit=False, bind=engine, class_=AsyncSession)

async def get_session():
    async  with AsyncLocalSession() as session:
        yield session