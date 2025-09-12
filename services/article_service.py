import schemas
from repositorys.sqlalchemy_article_repo import SqlalchemyArticleRepo
from fastapi import HTTPException
from repositorys.sqlalchemy_tag_repo import SqlAlchemyTagRepo
from database.models import Article,Pics


async def publish(model:schemas.CreateArticle, repo:SqlalchemyArticleRepo, tag_repo:SqlAlchemyTagRepo):
    
    tags=await tag_repo.get_all_tags()
    existing_tags=[tag.name for tag in tags]
    if model.tags:
        for tag in model.tags:
            if tag not in existing_tags:
                raise HTTPException(status_code=409, detail="Hubo un problema con los tags enviados, compruebe que los tags existan")
    
    existing_title=await repo.get_by_title(model.title)
    if existing_title:
        raise HTTPException(status_code=409, detail="No se ha podido crear el artículo porque ya existe uno con ese nombre")

    article=Article(
        title=model.title,
        content=model.content,
        autor_id=model.autor_id,
        tags=[tag for tag in tags if tag.name in model.tags],
        
    )
    if model.pics:
        for pi in model.pics:
            pic=Pics(link=pi)
            article.pics.append(pic)


    return await repo.save(article)
    


async def delete(article_id:int, repo:SqlalchemyArticleRepo):
    article=await repo.get_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="No se encontró ningún artículo")
    try:
        await repo.delete(article)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo eliminar el artículo: {e}")
    
