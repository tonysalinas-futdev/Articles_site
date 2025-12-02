from pydantic import BaseModel, Field, field_validator,ConfigDict,model_validator
from datetime import datetime
from typing import List,Optional
import re
from fastapi import HTTPException



class LikeSchema(BaseModel):
    id: int
    article_id:int
    user_id:int
    model_config = ConfigDict(from_attributes=True)
    




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

class ArticleList(BaseModel):
    id:int
    title:str
    content:str
    date:datetime
    in_favorites:bool
    autor_id:int
    pics:Optional[List[str]]=None
    tags:Optional[List[TagBase]]=None
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
    in_favorites:datetime
    autor_id:int
    is_suspended:bool
    pics:Optional[List[str]]=None
    tags:Optional[List[TagBase]]=None
    comments:Optional[List[Comments]]=None
    likes:Optional[List[LikeSchema]]=None
    total_likes:Optional[int]=0
    

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
    in_favorites:bool
    date:datetime
    comments:Optional[List[Comments]]=None
    autor:WriterArticleInfo
    likes:Optional[List[LikeSchema]]=None
    total_likes:Optional[int] = 0
    @model_validator(mode="after")
    def set_total_likes(cls, values):
        values.total_likes = len(values.likes) if values.likes else 0
        return values
    model_config = ConfigDict(from_attributes=True)


class CreateComment(BaseModel):
    
    text:str=Field(
        ...,
        min_length=1,
        max_length=4000
    )

class GetAllPaginated(BaseModel):
    next_cursor:Optional[int]=None
    items:List[ArticleList]
    has_more:bool
    model_config = ConfigDict(from_attributes=True)

class SearchByFilters(BaseModel):
    autor_id:Optional[int]=None
    tags:Optional[List[str]]=None
    title:Optional[str]=None



class MsgResponse(BaseModel):
    message:str

