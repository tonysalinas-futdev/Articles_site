import app.user_schemas as user_schemas
from fastapi import HTTPException
from app.database.models import User,Writer,Admin
from app.jwt_utils import  generate_token,refresh_token
from app.repositorys.sqlalchemycrud import SqlAlchemyUserRepo
from app.utils import hash_password, verify_password
from datetime import datetime
from typing import Union
#Función para generar el access_token y el refresh token con los datos del usuario , las separamos para no repetir la lógica en en login y el signin
async def generate_token_and_refresh(user:User):
    #Generamos el access
    token=generate_token(user.firstname, user.user_type,user.email, user.id)
    #Generamos el refresh
    refresh=refresh_token(user.id)
    #Construimos el esquema con los datos a devolver
    schema=user_schemas.UserSend(
        id=user.id,
        firstname=user.firstname,
        lastname=user.lastname,
        email=user.email,
        joined=user.joined,

    )

    return {
        "access_token":token,
        "token_type":"Bearer",
        "refresh_token":refresh,
        
        "user_data":schema
    }
    


#Service encargado de la creación de cuentas
async def create_user(model:user_schemas.UserCreate, repo:SqlAlchemyUserRepo):
    #Convertimos el modelo a un diccionario
    data=model.model_dump()
    #Confirmamos que no existe una cuenta ya con ese email
    existing=await repo.get_by_email_or_id(email=data["email"])
    if existing:
        raise HTTPException(status_code=409, detail="Ya existe ese email")
    #Asignamos la contraseña hasheada
    data["password"]=hash_password(data.get("password"))
    #Construimos el objeto usuario
    user=User(
        **data

    )
    #Lo guardamos
    await repo.save(user)
    #Generamos los datos
    return await generate_token_and_refresh(user)


#Service encargado de el login
async def signin(model:user_schemas.UserSignIn, repo:SqlAlchemyUserRepo):
    #Obtenemos al usuario según el email recibido
    user=await repo.get_by_email_or_id(email=model.email)
    if not user:
        raise HTTPException(status_code=401, detail="Error en las credenciales")
    
    #Comparamos la contraseña hasheada con la enviada
    if not verify_password(model.password,user.password):
        raise HTTPException(status_code=401, detail="Error en las credenciales")
    
    #Generamos los datos
    return await generate_token_and_refresh(user)

async def update_password(user_id,model:user_schemas.UpdatePassword, repo:SqlAlchemyUserRepo):
    user=await repo.get_by_email_or_id(id=user_id)
    if verify_password(model.password, user.password):
        if verify_password(model.new_password,user.password):
            raise HTTPException(status_code=409,detail="La contraseña nueva debe ser distinta a la anterior")
        
        user.password=hash_password(model.new_password)
        await repo.commit_and_refresh(user)
        return True
    else:
        raise HTTPException(status_code=401,detail="Contraseña incorrecta")


#Lógica para editar el perfil del usuario
async def edit(user_id:int, model:Union[user_schemas.UserUpdate,user_schemas.WriterProfileUpdate],repo:SqlAlchemyUserRepo):
    user=await repo.get_by_email_or_id(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="No se ha encontrado ese usuario")
    data=model.model_dump(exclude_none=True)
    for key , value in data.items():
        setattr(user, key, value)
    await repo.commit_and_refresh(user)
    return user

#Función para cambiar el rol de un usuario , en este caso debemos crear otro , con los datos del anterior , ya que la clase cambia
async def change_role(user_id:int , model:user_schemas.ChangeRole, repo:SqlAlchemyUserRepo):
    #Obtenemos al usuario por su id
    user=await repo.get_by_email_or_id(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="No se ha encontrado ese usuario")
    #Listamos las clases disponibles
    classes=[Writer,Admin,User]

    #
    new_class=None

    #Iteramos sobre las clases y buscamos cuál coincide con el nombre del rol enviado por el cliente
    for class_ in classes:
        if class_.__name__==model.new_role.capitalize():
            new_class=class_
            break
    if new_class:
        #Si la hay , obtenemos todos los atributos del usuario viejo y los transferimos al nuevo, pero con su nueva clase
        data={
            "firstname":user.firstname,
            "lastname":user.lastname,
            "joined":user.joined,
            "password":user.password,
            "id":user.id,
            "email":user.email



            
        }
        data["user_type"] = model.new_role
        new_user=new_class(
            firstname=data.get("firstname"),
            lastname=data.get("lastname"),
            id=data.get("id"),
            joined=data.get("joined"),
            password=data.get("password"),
            email=data.get("email")


        )

        await repo.delete(user.id)
        await repo.save(new_user)

        return new_user
    else:
        raise HTTPException(status_code=409, detail="El rol introducido no es válido")    


async def verify_otp(code:int, repo:SqlAlchemyUserRepo):
    token=await repo.get_otp(code)
    user_id=token.user_id
    if not token:
        raise HTTPException(status_code=404, detail="Código incorrecto")
    ahora=datetime.now()
    if ahora>token.exp_time or token.expired==True:
        raise HTTPException(status_code=409, detail="Token expirado o inválido")

    
    token.expired=True
    await repo.commit_()
    return user_id

