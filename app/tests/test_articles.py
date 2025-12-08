
from app.database.models import Article, Tags,Pics
import pytest
from sqlalchemy.exc import IntegrityError




#Test para probar la función para persistir los artículos en la bd en el caso positivo
@pytest.mark.parametrize(
    "tag, title, content ,pics, autor_id",
[
    (None, "Java para noobs", "afsdfas", None, 3),
    (["#python"], "Python para principiantes", "afsfdgdfgdfg", ["dfsdfsd", "adfsdfas"], 4),
],
)
@pytest.mark.asyncio
async def test_save_succes(tag, title, content, pics, autor_id,get_article_repo):
    article=Article(
        title=title,
        content=content,
        autor_id=autor_id,

    )
    if tag:
        article.tags.extend([Tags(name=ta) for ta in tag])
    if pics:
        article.pics.extend([Pics(link=pic) for pic in pics])


    
    saved=await get_article_repo.save(article)
    assert saved.id is not None


#Test para probar la función para persistir los artículos en la bd en el caso negativo

@pytest.mark.parametrize(
    "tag, title, content ,pics, autor_id",
[
    (None, None, "afsdfas", None, 3),
    
],
)
@pytest.mark.asyncio
async def test_save_failed(tag, title, content, pics, autor_id,get_article_repo):
    article=Article(
        title=title,
        content=content,
        autor_id=autor_id,

    )
    if tag:
        article.tags.extend([Tags(name=ta) for ta in tag])
    if pics:
        article.pics.extend([Pics(link=pic) for pic in pics])


    with pytest.raises(IntegrityError):
        assert await get_article_repo.save(article)
    



