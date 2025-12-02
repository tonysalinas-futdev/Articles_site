import schemas
from repositorys.sqlalchemy_article_repo import SqlalchemyArticleRepo
from fastapi import HTTPException
from repositorys.sqlalchemy_tag_repo import SqlAlchemyTagRepo
from database.models import Article,Pics,Comment,Like


#Service para crear un artículo
async def publish(autor_id:int,model:schemas.CreateArticle, repo:SqlalchemyArticleRepo, tag_repo:SqlAlchemyTagRepo):
    #Obtenemos todos los tags disponibles para saber si los enviados por el cliente son válidos 
    tags=await tag_repo.get_all_tags()
    existing_tags=[tag.name for tag in tags]
    if model.tags:
        for tag in model.tags:
            if tag not in existing_tags:
                raise HTTPException(status_code=409, detail="Hubo un problema con los tags enviados, compruebe que los tags existan")
    
    #Verificamos que no existe ya un artículo con ese título
    existing_title=await repo.get_by_title(model.title)
    if existing_title:
        raise HTTPException(status_code=409, detail="No se ha podido crear el artículo porque ya existe uno con ese nombre")

    #Armamos el objeto artículo
    article=Article(
        title=model.title,
        content=model.content,
        autor_id=autor_id,
        tags=[tag for tag in tags if tag.name in model.tags],
        
    )
    #Creamos los objetos Pics
    if model.pics:
        for pi in model.pics:
            pic=Pics(link=pi)
            article.pics.append(pic)


    return await repo.save(article)
    

#Service para eliminar un artículo
async def delete(article_id:int, repo:SqlalchemyArticleRepo):
    article=await repo.get_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="No se encontró ningún artículo")
    try:
        await repo.delete(article)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo eliminar el artículo: {e}")
    

async def coment(user_id:int,article_id:int, repo:SqlalchemyArticleRepo,model:schemas.Comments):
    article=await repo.get_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="No se encontró ningún artículo")
    obj_comment=Comment(
        text=model.text,
        article_id=article_id,
        user_id=user_id
        )
    
    await repo.save(obj_comment)
    
    

    return {"message":"Comentario creado exitosamente"}

async def react(article_id: int, user_id:int, repo:SqlalchemyArticleRepo):
    existing_like=await repo.get_like(user_id, article_id)
    if existing_like:
        await repo.delete(existing_like)
        return {"message":"Ha eliminado su reacción"}
    like=Like(
        user_id=user_id,
        article_id=article_id
    )
    await repo.save(like)
    
    return {"message":"Ha reaccionado correctamente"}

async def add_to_favorites(article_id:int,repo:SqlalchemyArticleRepo):
    article=await repo.get_by_id(article_id)
    if article.in_favorites==False:
        article.in_favorites=True
        await repo.commit_()
        return {"message":"Artículo añadido a favoritos"}
    
    else:
        article.in_favorites=False
        await repo.commit_()

        return {"message":"Artículo eliminado de favoritos"}
    
    