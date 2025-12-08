
import pytest
from app.services.article_service import delete
from app.database.models import Article, User,Writer
from app.main import app



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
    assert response.json()["total_likes"]==0
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

#Vamos a testear que el usuario intente obtener su perfil sin estar autenticado
@pytest.mark.asyncio
async def test_failed_get_profile(get_client):
    response=await get_client.get("/users/get_profile")
    assert response.status_code==401
    
#Testteamos la ruta encargada del login , vamos a usar a los dos usuarios que definimos en el conftest
@pytest.mark.asyncio
async def test_login_success(users_data, get_client):
    admin_data={
        "email":"pedorperez@gmail.com",
        "password":"Jacd#1234yg"
    }

    writer_data={
        "email":"kroosismo@gmail.com",
        "password":"Jacd#124yg",
    }

    admin_login=await get_client.post("/users/login",json=admin_data)
    writer_login=await get_client.post("/users/login",json=writer_data)
    
    assert admin_login.status_code==200
    assert writer_login.status_code==200
    assert admin_login.json()["user_data"]["firstname"]=="Pedro"
    assert writer_login.json()["user_data"]["firstname"]=="Tony"
    assert writer_login.json()["access_token"] is not None
    assert admin_login.json()["access_token"] is not None

#Vamos a probar a mandar credenciales incorrectas a la ruta de login , primero un email incorrecto y luego una contraseña incorrecta
@pytest.mark.asyncio
async def test_login_negative(users_data, get_client):
    writer_data={
        "email":"kroosis@gmail.com",
        "password":"Jacd#124yg",
    }

    admin_data={
        "email":"pedorperez@gmail.com",
        "password":"Jacd#123g"
    }

    writer_login=await get_client.post("/users/login",json=writer_data)
    admin_login=await get_client.post("/users/login",json=admin_data)


    assert writer_login.status_code==401
    assert writer_login.json()=={"detail":"Error en las credenciales"}
    assert admin_login.json()=={"detail":"Error en las credenciales"}
    assert admin_login.status_code==401







#Test para el endpoint crear una cuenta , caso positivo
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


#Test para el endpoint crear una cuenta , caso negativo, probaremos no mandar nombre, no mandar apellidos, una contraseña incorrecta y un email que ya existe

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
            
            

#Test de caso positivo para la ruta que nos devuelve otro access_token
@pytest.mark.asyncio
async def test_refresh_route(get_client, get_login_writer):
    response=await get_client.post("/users/refresh", json={"token":get_login_writer["refresh_token"]})
    assert response.status_code==200
    assert response.json()["access_token"] is not None
    assert response.json()["token_type"]=="Bearer"
    assert response.json()["user_data"] is not None

#Test de caso positivo para la ruta que nos permite editar nuestro perfil, probaremos con varias combinaciones posibles
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

#Vamos a probar editar nuestro perfil sin estar autenticados , nos dirá que no estamos autorizados
@pytest.mark.asyncio
async def test_edit_profile_route_failed(get_client, get_login_writer):
    data={
        "firstname":"Manuel",
        "lastname":"Castro",
        "email":"emailexample@gmail.com",
        "bio":"Periodista"
    }
    response=await get_client.put("/users/edit_profile", json=data)
    assert response.status_code==401


@pytest.mark.asyncio
async def test_change_password_route(get_client, get_login_writer):
    data={
        "password":"Jacd#124yg",
        "new_password":"1234567Ab#"
    }
    response=await get_client.put("/users/change_password", json=data, headers={"Authorization":f"Bearer {get_login_writer["access_token"]}"})
    assert response.status_code==200
    assert response.json()=={"message":"La contraseña fue actualizada exitosamente"}


#Test para probar las ruta de cambio de contraseña , caso negativo , vamos a probar mandar la contraseña del usuario incorrecta y luego mandar la nueva , idéntica a la vieja
@pytest.mark.parametrize("password, new_password, status_code, response_content",[
    ("12345678#Ja", "1234567Ab#",401,{"detail":"Contraseña incorrecta"}),
    ("Jacd#124yg", "Jacd#124yg",409,{"detail":"La contraseña nueva debe ser distinta a la anterior"}),
])
@pytest.mark.asyncio
async def test_change_password_route_failed(password,new_password,status_code,response_content,get_client, get_login_writer):
    data={
        "password":password,
        "new_password":new_password
    }
    response=await get_client.put("/users/change_password", json=data, headers={"Authorization":f"Bearer {get_login_writer["access_token"]}"})
    assert response.status_code==status_code
    assert response.json()==response_content
    

#Test para el endpoint para dejar un comentario, caso positivo
@pytest.mark.asyncio
async def test_comment(article_data, get_client, get_login_admin):
    data={
        "text":"Increíble artículo, me gustó mucho"
    }
    response=await get_client.post("users/comment/1", json=data,headers={"Authorization":f"Bearer {get_login_admin["access_token"]}"})
    assert response.status_code==201
    assert response.json()=={"message":"Se ha creado su comentario exitosamente"}

#Test para el endpoint para dejar un comentario, caso negativo, no se encuentra un artículo con ese id

@pytest.mark.asyncio
async def test_comment_negative(article_data, get_client, get_login_admin):
    data={
        "text":"Increíble artículo, me gustó mucho"
    }
    response=await get_client.post("users/comment/3", json=data,headers={"Authorization":f"Bearer {get_login_admin["access_token"]}"})
    assert response.status_code==404
    assert response.json()=={"detail":"No se encontró ningún artículo"}

#Vamos a testear la ruta para obtener todos los artículos, son un total de 15 , veremos que pasa cuando obtenemos 10 y que pasa luego cuando solo quedan 5
@pytest.mark.asyncio
async def test_get_all_articles(data_in_db, get_client,get_session_override):
    response=await get_client.get("/article/get_all")
    response2=await get_client.get("/article/get_all?cursor=10")
    assert response.status_code==200
    assert response2.status_code==200
    assert response2.json()["next_cursor"]==None
    assert response2.json()["has_more"]==False
    assert len(response2.json()["items"])==5

    assert response.json()["next_cursor"]==10
    assert response.json()["has_more"]==True
    assert len(response.json()["items"])==10

#Test para la ruta que nos devuelve los datos filtrados según el id del autor, título o etiquetas, vamos a verificar que en cada artículo esté la etiqueta #java y que ademas la palabra "python esté incluída en cada título"
@pytest.mark.asyncio
async def test_filter_articles(data_in_db, get_client,get_session_override):
    #Data para los tags
    data={
        "tags":["#java"],
        "title":"python"
    }

    response=await get_client.post("/article/filter", json=data)


    articles=response.json()["items"]
    tags=[article.get("tags") for article in articles]
    assert all("python" in article.get("title") for article in articles )
    assert response.status_code==200
    for lista in tags:
        assert any("#java"==tag.get("name") for tag in lista)
    

#Testeamos la ruta con la cual un admin puede cambiar el rol de un usuario
@pytest.mark.asyncio
async def test_promote_user( get_client, get_login_admin, users_data,get_user_repo):
    #Vamos a cambiar el rol de nuestro usuario creado en el conftest con id=2 de writer a user
    data={
        "new_role":"user"
    }
    response=await get_client.put("/admin/promote_user/2", json=data, headers={"Authorization":f"Bearer {get_login_admin["access_token"]}"})
    #Vamos a comprobar que efectivamente se cambió el rol y además es el mismo usuario
    user2=await get_user_repo.get_by_email_or_id(id=2)
    assert response.status_code==200
    assert response.json()=={"message":f"Ha cambiado el rol del usuario Tony Salinas exitosamente"}
    assert user2.user_type=="user"
    assert user2.firstname=="Tony"
    assert user2.lastname=="Salinas"


#Testeamos la ruta con la cual un admin puede cambiar el rol de un usuario caso negativo, vamos a probar a intentar acceder a la ruta con un usuario que no es admin y a intentar cambiar el rol de un usuario que no existe, las validaciones para aceptar un role válido ya las hace pydantic, usé ENUM
@pytest.mark.asyncio
async def test_promote_user_negative( get_client, get_login_admin, get_login_writer, users_data,get_user_repo):
    #Vamos a cambiar el rol de nuestro usuario creado en el conftest con id=2 de writer a user
    data={
        "new_role":"user"
    }
    response=await get_client.put("/admin/promote_user/2", json=data, headers={"Authorization":f"Bearer {get_login_writer["access_token"]}"})
    response2=await get_client.put("/admin/promote_user/3", json=data, headers={"Authorization":f"Bearer {get_login_admin["access_token"]}"})
    data2={
        "new_role":"superuser"
    }
    response3=await get_client.put("/admin/promote_user/3", json=data2, headers={"Authorization":f"Bearer {get_login_admin["access_token"]}"})
    
    assert response.status_code==401
    assert response.json()=={"detail":"Usted no tiene autorización para acceder a esta ruta"}
    assert response2.status_code==404
    assert response2.json()=={"detail":"No se ha encontrado ese usuario"}

@pytest.mark.asyncio
async def test_get_all_users(users_in_db, get_client, get_login_admin):
    response=await get_client.get("/admin/get_all_users",headers={"Authorization":f"Bearer {get_login_admin["access_token"]}"})

    assert response.status_code==200
    assert response.json()["next_cursor"]==15
    assert response.json()["has_more"]==True
    assert len(response.json()["items"])==15


#Testeamos que el endpoint para obtener un usuario por su id  nos devuelve datos correctos de ese usuario
@pytest.mark.asyncio
async def test_get_one_user(get_client, get_login_admin,users_data,get_user_repo):
    response=await get_client.get("admin/get_user/2",headers={"Authorization":f"Bearer {get_login_admin["access_token"]}"})
    assert response.status_code==200
    assert response.json()["id"]==2
    assert response.json()["email"]=="kroosismo@gmail.com"



#Testeamos que el endpoint para obtener un usuario por su id no nos deja cceder si no somos admin y que además nos devuelve un error si el usuario no existe
@pytest.mark.asyncio
async def test_get_one_user_failed(get_client,get_login_admin ,get_login_writer,users_data,get_user_repo):
    response=await get_client.get("admin/get_user/2",headers={"Authorization":f"Bearer {get_login_writer["access_token"]}"})

    response2=await get_client.get("admin/get_user/3",headers={"Authorization":f"Bearer {get_login_admin["access_token"]}"})
    assert response.status_code==401
    assert response.json()=={"detail":"Usted no tiene autorización para acceder a esta ruta"}
    assert response2.status_code==404
    assert response2.json()=={"detail":"No se ha encontrado ningún usuario con ese id"}
    


@pytest.mark.asyncio
async def test_react_to_article(get_client, get_login_admin,users_data,get_article_repo,article_data, get_login_writer):
    response=await get_client.post("users/like/1",headers={"Authorization":f"Bearer {get_login_admin["access_token"]}"})
    response2=await get_client.post("users/like/1",headers={"Authorization":f"Bearer {get_login_writer["access_token"]}"})
    response3=await get_client.post("users/like/1",headers={"Authorization":f"Bearer {get_login_admin["access_token"]}"})
    article= await get_article_repo.get_by_id(1)
    assert article.id==1
    assert len(article.likes)==1

    assert response.status_code==200
    assert response2.status_code==200
    assert response3.status_code==200

    assert response.json()=={"message":"Ha reaccionado correctamente"}


