import user_schemas
import pytest
from services.article_service import delete
from database.models import Article, User,Writer
from main import app
from fastapi import HTTPException


#Test positivo la ruta para la creación de un artículo
@pytest.mark.asyncio
async def test_create_article(get_session_override,get_client,get_article_repo, users_data,get_login_writer):
    


    data={
  "title": "Pythongfgfdgdfg",
  "content": "fgdfgdfg",
  "pics": [
    "string"
  ],
"autor_id":get_login_writer["user_data"]["id"]
}
    
    response=await get_client.post("/writers/create",json=data, headers={"Authorization":f"Bearer {get_login_writer["access_token"]}" } )
    
    assert response.status_code==201
    assert response.json()=={"message":"Artículo creado exitosamente"}
        


#Test positivo la ruta para la creación de un artículo (Artículo sin título , un tag mal escrito y un título que ya existe)

@pytest.mark.parametrize("title, content, pics,tags ,autor_id, status_code",[
(None,"sdfsgsg",["sdsgsgfs"],[], 1,422),
("JAS","sdfsgsg",[],["python"], 1,409),
("Hola Python","sdfsgsg",[],[],1,409),

])
@pytest.mark.asyncio
async def test_create_article_failed(title, content, pics, tags , autor_id , status_code ,get_session_override,get_client,users_data,get_login_writer, article_data):
    data={
    "title": title,
    "content": content,
    "pics": pics,
    "tags":tags,
    "autor_id": autor_id
}
    
    response=await get_client.post("/writers/create", json=data, headers={"Authorization":f"Bearer {get_login_writer["access_token"]}"})
    assert response.status_code==status_code



#Test positivo para la ruta que nos devuelve un artículo según su id
@pytest.mark.asyncio
async def test_get_article_by_id(get_client, article_data):
    response=await get_client.get("article/get_one/1")
    assert response.json()["id"]==1
    assert response.status_code==200

#Test negativo para la ruta que nos devuelve un artículo según su id

@pytest.mark.asyncio
async def test_fail_get_article_by_id(get_client, article_data):
    response=await get_client.get("article/get_one/2")
    assert response.status_code==404
    assert response.json()=={"detail": "No se ha podido encontrar ese artículo"}


#Test para que un usuario autenticado obtenga su perfil
@pytest.mark.asyncio
async def test_get_profile(get_client, get_login_admin):
    response=await get_client.get("/users/get_profile", headers={"Authorization":f"Bearer {get_login_admin["access_token"]}"})
    assert response.status_code==200
    assert response.json()["id"]==get_login_admin["user_data"]["id"]


@pytest.mark.asyncio
async def test_failed_get_profile(get_client):
    response=await get_client.get("/users/get_profile")
    assert response.status_code==401
    


@pytest.mark.parametrize("firstname, lastname, email, password",[
    ("Tony","Chao Salinas", "ejemplsdasdo@gmail.com", "1234567La#"),
    ("Carlos Albert","Gonzalez", "ejemplo2@gmail.com", "1234jgjkg7La#"),
])
@pytest.mark.asyncio
async def test_signup(firstname,lastname,email,password, get_client, get_session_override):
    data={
        "firstname":firstname,
        "lastname":lastname,
        "email":email,
        "password":password
    }

    response=await get_client.post("/users/signup", json=data)
    token=response.json()["access_token"]
    refresh=response.json()["refresh_token"]

    assert response.status_code==201
    assert token is not None and refresh is not None



@pytest.mark.parametrize("firstname, lastname, email, password",[
    (None,"Chao Salinas", "ejemplsdasdo@gmail.com", "1234567La#"),
    ("Carlos Albert",None, "ejemplo2@gmail.com", "1234jgjkg7La#"),
    ("Edu Camavinga",None, "ejemplo3@gmail.com", "1234"),
    ("Gonzalo","Gonzalez", "ejemplo4@gmail.com", "1234jsaas#A"),


])
@pytest.mark.asyncio
async def test_signup_failed(firstname,lastname,email,password, get_client, get_session_override, get_test_session):
    if firstname=="Gonzalo":
        user=User(
        firstname="Mario",
        lastname="Perez",
        email="ejemplo4@gmail.com",
        password="1234567La#"

    )
        
        get_test_session.add(user)
        await get_test_session.commit()


    data={
        "firstname":firstname,
        "lastname":lastname,
        "email":email,
        "password":password
    }

    response=await get_client.post("/users/signup", json=data)
    if firstname!="Gonzalo":
        assert response.status_code==422
    
    if firstname=="Gonzalo":
        assert response.status_code==409
        assert response.json()["detail"]=="Ya existe ese email"
            
            


@pytest.mark.asyncio
async def test_refresh_route(get_client, get_login_writer):
    response=await get_client.post("/users/refresh", json={"token":get_login_writer["refresh_token"]})
    assert response.status_code==200
    assert response.json()["access_token"] is not None
    assert response.json()["token_type"]=="Bearer"
    assert response.json()["user_data"] is not None


@pytest.mark.parametrize("firstname, lastname, email, bio",[
    ("Omar", None, None, None),
    (None, "Diaz", None, None),
    (None, None, "ejemplousuario@gmail.com", None),
    (None, None, None, "Programador Backend"),
    ("Omar", "Diaz","ejemplousuario@gmail.com", "Programador Backend"),
] )
@pytest.mark.asyncio
async def test_edit_profile_route(firstname,lastname,email,bio,get_client, get_login_writer):
    data={
        "firstname":firstname,
        "lastname":lastname,
        "email":email,
        "bio":bio
    }
    response=await get_client.put("/users/edit_profile", json=data, headers={"Authorization":f"Bearer {get_login_writer["access_token"]}"})
    assert response.status_code==200