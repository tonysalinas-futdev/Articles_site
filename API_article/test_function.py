from repositorys import SqlalchemyArticleRepo
from database.models import Article
import pytest
import pytest_asyncio
import schemas
from typing import List

from database.database import AsyncLocalSession
from fastapi import HTTPException
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
from faker import Faker
import random

#Definimos el fixture para entregar el service junto con la session
@pytest_asyncio.fixture
async def repo():
    async with AsyncLocalSession() as session:
        yield SqlalchemyArticleRepo(session)
        
    
    


#Fixture con el esquema pydantic y atributos dinámicos para el parametrize
@pytest.fixture
def data():
    def create(title,content,tags,autor_id,pics):
        return schemas.CreateArticle(
        title=title,
        content=content,
        tags=tags,
        pics=pics,
        autor_id=autor_id
        
    )
    return create

#Test para validar la creación exitosa de un artículo
@pytest.mark.parametrize("title, content, tags, pics, autor_id",[
    ("Python para noobs", "sdsgdsg",[],["afsddfgsd"], 1 ),
    ("Python para inteñigentes", "sdsgdfgdfgdsg",["programación", "python", "fastapi"],None, 2 ),
    ("Python nivel intermedio", "sdsgdfgdfgdfdsg",["programación"],[], 4 )
])
@pytest.mark.asyncio
async def test_create(data, repo ,title, content,tags,autor_id,pics ):
    article=data(title=title, content=content,tags=tags,autor_id=autor_id, pics=pics)
    assert await repo.create_article(article)
    

#Test para validar varios casos de una creación fallida
@pytest.mark.parametrize("title, content, tags, pics, autor_id, resultado",[
    (None, "sdsgdsg",[],["afsddfgsd"], 1, ValidationError ),
    ("Python para inteñigentes", None,["programación", "python", "fastapi"],None, 2, ValidationError ),
    ("Python nivel intermedio", "sdsgdfgdfgdfdsg",["programación"],[], 4 , HTTPException),
    ("Python", "sdsgdfgdfgdfdsg",["programación"],[], 4 , HTTPException)

])
@pytest.mark.asyncio
async def test_create_failed(data,repo, title, content,pics,autor_id,resultado,tags):
    #Creamos otro artículo llamado python para testear la duplicación de títulos
    if title=="Python":
        old_article=schemas.CreateArticle(
        title="Python",
        content="asdaf",
        tags=[],
        pics=[],
        autor_id=1

    )
        await repo.create_article(old_article)
    
    if resultado==ValidationError:
        with pytest.raises(ValidationError):
            data(title=title, content=content,tags=tags,autor_id=autor_id, pics=pics)
    else:
        with pytest.raises(resultado):
            article=data(title=title, content=content,tags=tags,autor_id=autor_id, pics=pics)
            assert await repo.create_article(article)
    




@pytest.mark.asyncio
async def test_get_by_id(repo,article_id=1):
    article=schemas.CreateArticle(
                title="Test",
        content="Lorem Ipsun",
        tags=[],
        pics=[],
        autor_id=1
    )
    await repo.create_article(article)

    assert await repo.get_by_id(article_id)

    with pytest.raises(HTTPException):
        await repo.get_by_id(999999)
    
    with pytest.raises(HTTPException):
        await repo.get_by_id("hola")
        

@pytest_asyncio.fixture
async def datas():
    fake=Faker()
    async with AsyncLocalSession() as session:
        for i in range(20):
            article=Article(
            title=fake.sentence(),
            content=fake.text(),
            pics=[],
            autor_id=random.randint(1,100)
        )


        
            session.add(article)
        await session.commit()

@pytest.mark.asyncio
async def test_get_all(datas, repo):
    response=await repo.get_all()
    assert isinstance(response, schemas.GetAllPaginated)
    assert response.has_more==True
    assert response.next_cursor==10
    
    assert len(response.items)==10
    for elemento in response.items:
        assert isinstance(elemento, schemas.SendArticleDetail)




