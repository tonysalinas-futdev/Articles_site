from pydantic import BaseModel, Field,EmailStr, field_validator, model_validator, ConfigDict
from typing import List,Optional
from app.schemas import ArticleBase
from datetime import datetime
from app.validators import password_validator, pattern_password_validation, name_validator
from enum import Enum



#Esquema con los datos de usuario que va a recibir el admin
class UserBase(BaseModel):
    id:int
    firstname:str
    lastname:str
    email: EmailStr
    user_type:str
    joined:datetime
    
    articles:Optional[List[ArticleBase]]=[]
    bio:Optional[str]=None


#Esquema para iniciar sesión
class UserSignIn(BaseModel):
    email:EmailStr
    password: str=password_validator()
    @field_validator("password")
    def validate_password(cls, valor):
        return pattern_password_validation(valor)




#Esquema para crear un usuario
class UserCreate(UserSignIn):
    firstname:str=name_validator()
    lastname:str=name_validator()
    email: EmailStr
    password:str=password_validator()
    @field_validator("password")
    def validate_password(cls, valor):
        return pattern_password_validation(valor)


#Esquema para el usuario base
class UserBaseSend(BaseModel):
    id:int
    firstname:str
    lastname:str
    email: EmailStr
    joined:datetime
    model_config = ConfigDict(from_attributes=True)

#Esquema para el usuario writer

class UserSend(UserBaseSend):
    articles:Optional[List[ArticleBase]]=None
    bio:Optional[str]=None
    profile_pic:Optional[str]=None
    model_config = ConfigDict(from_attributes=True)


#Esquema para enviar la info cuando el usuario se loguee
class SignInData(BaseModel):
    access_token:str
    token_type:str
    refresh_token:str
    user_data:UserSend



#Esquema para recibir datos paginados
class GetAllPaginated(BaseModel):
    next_cursor:Optional[int]=None
    has_more:bool
    items:List[UserSend]
    

#Esquema para actualizar la info del usuario
class UserUpdate(BaseModel):
    firstname:Optional[str]=None
    lastname:Optional[str]=None
    email: Optional[EmailStr]=None
    

#Esquema para actualizar la info del escritor
class WriterProfileUpdate(UserUpdate):
    bio:Optional[str]=None
    profile_pic:Optional[str]=None


#Esquema para cambiar la contraseña
class UpdatePassword(BaseModel):
    password: str=password_validator()

    
    new_password:str=password_validator()
    
    @field_validator("new_password","password")
    def validate_password(cls, valor):
        return pattern_password_validation(valor)
    
    
    

#Esquema para refrescar el access token
class TokenRefreshResponse(BaseModel):
    access_token:str
    token_type:str
    user_data: UserSend

#Definimos los valores elegibles para los roles
class TypeUser(str, Enum):
    user="user"
    admin="admin"
    writer="writer"

class ChangeRole(BaseModel):
    new_role:TypeUser

class NewPassword(BaseModel):
    password: str=password_validator()