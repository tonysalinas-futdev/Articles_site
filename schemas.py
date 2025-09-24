from pydantic import BaseModel, Field, field_validator,ConfigDict
from datetime import datetime
from typing import List,Optional
import re
from fastapi import HTTPException

#Esquema con la informacion del autor que será mostrada en los detalles del artículo
class WriterArticleInfo(BaseModel):
    firstname:str
    lastname:str
    bio:Optional[str]=None
    model_config = ConfigDict(from_attributes=True)


#Clase para crear un comentario
class Comments(BaseModel):
    id:int
    text:str=Field(
        
        max_length=4000
    )
    


class Pics(BaseModel):
    link:str
    model_config = ConfigDict(from_attributes=True)


class TagBase(BaseModel):
    id:int
    name:str
    model_config = ConfigDict(from_attributes=True)



class CreateTag(BaseModel):
    name:str=Field(...,
                description="Crea una etiqueta para tu artículo , debe comenzar con #, sin espacios, todo en minúscula y de 1 a 55 caracteres",
                examples=["#python", "#java", "#programacion"]
                
                )
    @field_validator("name")
    def tag_validator(cls, value):
        pattern=r"^#(?!.*\s)[a-z]{1,55}$"
        if not re.fullmatch(pattern,value):
            raise HTTPException(status_code=409, detail="Fallo en la creación de la etiqueta")
        return value


class ArticleBase(BaseModel):
    id:int
    title:str
    content:str
    date:datetime
    autor_id:int
    is_suspended:bool
    pics:Optional[List[str]]=None
    tags:Optional[List[TagBase]]=None
    comments:Optional[List[Comments]]=None
    

class CreateArticle(BaseModel):
    title:str=Field(
        ...,
        description="Título del artículo, debe ser único"
        )

    content:str=Field(
        ...
    )
    pics:Optional[List[str]]=None
    tags:Optional[List[str]]=None



class SendArticleDetail(BaseModel):
    id:int
    title:str
    content:str
    autor_id:int
    pics:Optional[List[Pics]]=None
    tags:Optional[List[TagBase]]=None
    date:datetime
    comments:Optional[List[Comments]]=None
    autor:WriterArticleInfo
    model_config = ConfigDict(from_attributes=True)


class CreateComment(BaseModel):
    
    text:str=Field(
        ...,
        min_length=1,
        max_length=4000
    )

class GetAllPaginated(BaseModel):
    next_cursor:Optional[int]=None
    items:List[SendArticleDetail]
    has_more:bool
    model_config = ConfigDict(from_attributes=True)

class SearchByFilters(BaseModel):
    autor_id:Optional[int]=None
    tags:Optional[List[str]]=None
    title:Optional[str]=None



class MsgResponse(BaseModel):
    message:str

