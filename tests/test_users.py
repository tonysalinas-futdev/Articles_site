import pytest

from repositorys.sqlalchemy_article_repo import SqlalchemyArticleRepo
from repositorys.sqlalchemycrud import SqlAlchemyUserRepo
from database.models import User, Writer, Admin
@pytest.mark.parametrize(
        "firstname, lastname, email, user_type, password",
        [("Pedro", "Gonzalez", "kroosismo0202@gmail.com", "user", "123456789"),
        ("Carlo", "Agustín", "kroosismo@gmail.com", "writer", "12345678910"),
        ("Tony", "Salinas Chao", "camavinguismo@gmail.com", "admin", "1234567891011")],
)
@pytest.mark.asyncio
async def test_save_users(firstname, lastname, email, user_type, password ,get_test_session, get_article_repo):
    if user_type=="user":
        user=User(
        firstname=firstname,
        lastname=lastname,
        email=email,
        user_type=user_type,
        password=password
    )
    if user_type=="admin":
                user=Admin(
        firstname=firstname,
        lastname=lastname,
        email=email,
        user_type=user_type,
        password=password
    )
    if user_type=="writer":
            user=Writer(
        firstname=firstname,
        lastname=lastname,
        email=email,
        user_type=user_type,
        password=password
    )
    assert await get_article_repo.save(user)


