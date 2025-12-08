import pytest
import pytest_asyncio
from app.database.models import Article, Tags,Pics, Admin, Writer,User
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.repositorys.sqlalchemy_article_repo import SqlalchemyArticleRepo
from app.repositorys.sqlalchemy_tag_repo import SqlAlchemyTagRepo
from app.repositorys.sqlalchemycrud import SqlAlchemyUserRepo
from app.database.database import Base
from faker import Faker
import random
import httpx
from app.main import app
from app.utils import hash_password, verify_password
from httpx import ASGITransport
from app.dependences import get_session 

#Variables para la base de datos de los test
DATABASE_URL="sqlite+aiosqlite:///:memory:"
engine=create_async_engine(DATABASE_URL, echo=True)
AsyncLocalSession=sessionmaker(engine, autoflush=False,class_=AsyncSession)

#Fixture para crear los modelos y limpiarla luego de cada test
@pytest_asyncio.fixture
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

#Fixture para obtener la sessión
@pytest_asyncio.fixture
async def get_test_session(create_db):
    async with AsyncLocalSession() as session:
        yield session

#Fixture para obtener el repositorio article

@pytest_asyncio.fixture
async def get_article_repo(get_test_session):
    return SqlalchemyArticleRepo(get_test_session)

#Fixture para obtener el repositorio user
@pytest_asyncio.fixture
async def get_user_repo(get_test_session):
    return SqlAlchemyUserRepo(get_test_session)

#Fixture para obtener el repositorio etiqueta
@pytest_asyncio.fixture
async def get_tag_repo(get_test_session):
    return SqlAlchemyTagRepo(get_test_session)



#Fixture para sobrescribir la dependencia original de la sesión para los test
@pytest_asyncio.fixture
def get_session_override(get_test_session):
    async def override():
        yield get_test_session
    app.dependency_overrides[get_session]=override
    yield  
    app.dependency_overrides.clear()



#fixture para obtener un cliente asíncrono de httpx
@pytest_asyncio.fixture
async def get_client():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport,base_url="http://test") as client:
        yield client

#Fixture para guardar dos artículos en la base de datos



#Fixture para guardar dos usuarios en la bd
@pytest_asyncio.fixture
async def users_data(get_session_override, get_article_repo):
    user=Admin(
        firstname="Pedro",
        lastname="García ",
        email="pedorperez@gmail.com",
        password=hash_password("Jacd#1234yg"))
    
    user2=Writer(
        firstname="Tony",
        lastname="Salinas",
        email="kroosismo@gmail.com",
        password=hash_password("Jacd#124yg"),
        user_type="writer",
        bio="")
    

    
    
    await get_article_repo.save(user)
    await get_article_repo.save(user2)



    return {"admin":user,
            "writer":user2,
            }

#Fixture para entregaar un usuario con permisos de escritor ya logueado
@pytest_asyncio.fixture
async def get_login_writer(users_data, get_client):
    data={
        "email":"kroosismo@gmail.com",
        
        "password":"Jacd#124yg"
    }
    login_response=await get_client.post("users/login", json=data)
    
    return login_response.json()

#Fixture para entregaar un usuario con permisos de administrador ya logueado

@pytest_asyncio.fixture
async def get_login_admin(users_data, get_client):
    data={
        "email":"pedorperez@gmail.com",
        
        "password":"Jacd#1234yg"
    }
    login_response=await get_client.post("users/login", json=data)
    
    return login_response.json()




@pytest_asyncio.fixture
async def article_data(get_test_session,users_data):


    article=Article(
        title="Hola Python",
        content="sdsdgsg",
        autor_id=users_data["writer"].id,

    )     
    get_test_session.add(article)
    await get_test_session.commit()
    await get_test_session.refresh(article)
    return article


@pytest_asyncio.fixture
async def data_in_db(get_test_session,get_tag_repo,get_user_repo):
    writer=Writer(
        firstname="Eduardo",
        lastname="Camavinga",
        email="example@gmail.com",
        password=hash_password("1234567Ja#")
    )
    await get_user_repo.save(writer)
    fake=Faker()
    #Creamos los tags para los artículos
    tags=["#python", "#java", "#programacion", "#software", "#go", "#fastapi", "#laravel","#django"]
    tags_add=[Tags(name=tag) for tag in tags]
    get_test_session.add_all(tags_add)
    await get_test_session.flush()

    #Creamos 15 artículos con datos random
    for i in range (15):
        article=Article(
            #Una oración aleatoria que además va a contener algunas palabras de la lista
            title=f"{i}{fake.sentence()}{random.sample(["python", "java", "fastapi", "Aprende a","top 10", "django"],1)}",
            #Texto falso
            content=fake.text(),
            
            autor_id=writer.id,
            date=fake.date_this_year(),
            


        )
        #Va a elelgir tags aleatorios de la lista de tags, la cantidad es dinámica
        article_tags=random.sample(tags_add, random.randint(1, len(tags)-1))
        article.tags.extend(article_tags)
        get_test_session.add(article)


    await get_test_session.commit()

@pytest_asyncio.fixture
async def users_in_db(get_test_session,get_user_repo):
    fake=Faker()
    for i in range(20):
        user=User(
            firstname=fake.first_name(),
            lastname=fake.last_name(),
            email=fake.unique.email(),
            password=fake.password()
        )
        get_test_session.add(user)
    await get_test_session.commit()