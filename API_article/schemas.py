from pydantic import BaseModel, Field, field_validator,ConfigDict
from datetime import datetime
from typing import List,Optional
import re
from fastapi import HTTPException

class Pics(BaseModel):
    link:str
    model_config = ConfigDict(from_attributes=True)
class TagBase(BaseModel):
    id:int
    name:str
    model_config = ConfigDict(from_attributes=True)

class CreateTag(BaseModel):
    name:str=Field(...,
                description="Crea una etiqueta para tu artículo , debe comenzar con #, sin espacios, todo en minúscula y de 1 a 55 caracteres")
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
    pics:Optional[List[str]]=None
    tags:Optional[List[str]]=None

class CreateArticle(BaseModel):
    title:str=Field(
        ...)

    content:str=Field(
        ...
    )
    pics:Optional[List[str]]=None
    tags:Optional[List[str]]=None
    autor_id:int


class SendArticleDetail(BaseModel):
    id:int
    title:str
    content:str
    autor_id:int
    pics:Optional[List[Pics]]=None
    tags:Optional[List[TagBase]]=None
    date:datetime
    
    
    model_config = ConfigDict(from_attributes=True)


class CreateComment(BaseModel):
    article_id:int=Field(...)
    text:str=Field(
        ...,
        min_length=1,
        max_length=800
    )

class GetAllPaginated(BaseModel):
    next_cursor:Optional[int]=None
    items:List[SendArticleDetail]
    has_more:bool

class SearchByFilters(BaseModel):
    autor_id:Optional[int]=None
    tags:Optional[List[str]]=None
    title:Optional[str]=None



class MsgResponse(BaseModel):
    message:str

