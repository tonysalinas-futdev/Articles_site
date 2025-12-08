import app.schemas as schemas
from fastapi import HTTPException
from app.repositorys.sqlalchemy_tag_repo import SqlAlchemyTagRepo
from app.database.models import Tags

#Función para crear etiquetas
async def create_tag(model:schemas.CreateTag, repo:SqlAlchemyTagRepo):
    existing_tag=await repo.get_by_name(model.name)
    if existing_tag:
        raise HTTPException(status_code=409, detail="Ya existe una etiqueta con ese nombre")
    
    tag=Tags(
        name=model.name
    )
    try:
        return await repo.save(tag)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar la etiqueta {e}")



#Función para eliminar etiquetas
async def delete_tag(tag_id:int, repo:SqlAlchemyTagRepo):
    tag=await repo.get_by_id(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")

    try:
        await repo.delete_tag(tag)
    except Exception :
        raise HTTPException(status_code=500, detail="Error al elimnar las etiquetas")