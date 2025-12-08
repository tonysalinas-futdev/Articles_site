from fastapi import APIRouter, Depends,status, Request,Body, HTTPException, Response
from app.repositorys.sqlalchemycrud import SqlAlchemyUserRepo
from app.dependences import get_users_repo,get_repo
from app.limiter_config import limiter
import app.user_schemas as user_schemas
from app.repositorys.sqlalchemy_article_repo import SqlalchemyArticleRepo
import app.schemas as schemas
from app.services.article_service import coment, react,add_to_favorites
from app.services.user_service import create_user, signin, generate_token_and_refresh, update_password, edit, verify_otp
from app.jwt_utils import get_current_user, verify_refresh
from app.utils import hash_password
from pydantic import EmailStr
from app.send_email import send_email
from fastapi import Request
from typing import Union
from typing import List


router_users=APIRouter(prefix="/users", tags=["Users"])
#Endpoint para loguearse
@limiter.limit("60/minute")
@router_users.post("/login", response_model=user_schemas.SignInData, status_code=status.HTTP_200_OK, summary="Ruta para que el cliente se loguee")
async def  login_(request:Request,model:user_schemas.UserSignIn, repo:SqlAlchemyUserRepo=Depends(get_users_repo)):
    return await signin(model, repo)


#Endpoint para crear una cuenta
@limiter.limit("60/minute")
@router_users.post("/signup", response_model=user_schemas.SignInData, status_code=status.HTTP_201_CREATED, summary="Ruta para la creación de cuentas")
async def  signup_(request:Request,model:user_schemas.UserCreate, repo:SqlAlchemyUserRepo=Depends(get_users_repo)):
    return await create_user(model, repo)
@router_users.get("/get_profile", response_model=user_schemas.UserSend, status_code=status.HTTP_200_OK, summary="Ruta para que el cliente después de estar logueado, obtenga los sus datos")
async def get_user(repo:SqlAlchemyUserRepo=Depends(get_users_repo), data=Depends(get_current_user)):
    user_id=data.get("id")
    return await repo.get_by_email_or_id(id=user_id)



#Endpoint para obtener otro access_token
@router_users.post("/refresh", response_model=user_schemas.TokenRefreshResponse, summary="Endpoint que recibe el refresh_token para generar un nuevo access", status_code=status.HTTP_200_OK)
async def refresh_tok(token:str=Body(..., embed=True), repo:SqlAlchemyUserRepo=Depends(get_users_repo)):
    user_id=verify_refresh(token)
    if user_id:
        user=await repo.get_by_email_or_id(id=user_id)
        if user:
            data:dict=await generate_token_and_refresh(user)
            data.pop("refresh_token", None)
            return data
    raise HTTPException(status_code=404, detail="No se ha encontrado ningún usuario")


#Ruta para cambiar de contraseña
@router_users.put("/change_password", response_model=schemas.MsgResponse, summary="Endpoint para que el usuario cambie su contraseña",status_code=status.HTTP_200_OK)
async def edit_password(model:user_schemas.UpdatePassword, repo:SqlAlchemyUserRepo=Depends(get_users_repo),data=Depends(get_current_user)):

    if await update_password(data.get("id"),model, repo):
        return {"message":"La contraseña fue actualizada exitosamente"}
    else:
        raise HTTPException(status_code=409, detail="No se ha podido actualizar la contraseña")


#Ruta para editar la información del perfil
@router_users.put("/edit_profile", response_model=schemas.MsgResponse, summary="Ruta para editar la información del perfil", status_code=status.HTTP_200_OK)
async def edit_profile(model:Union[user_schemas.UserUpdate, user_schemas.WriterProfileUpdate],  data=Depends(get_current_user),repo:SqlAlchemyUserRepo=Depends(get_users_repo)):
    await edit(data.get("id"),model, repo)

    return {"message":"Ha actualizado su perfil exitosamente"}



#Ruta para comentar
@router_users.post("/comment/{article_id}", response_model=schemas.MsgResponse, summary="Ruta para comentar un artículo", status_code=status.HTTP_201_CREATED )
async def create_comment(article_id:int, model:schemas.CreateComment,service:SqlalchemyArticleRepo=Depends(get_repo),data=Depends(get_current_user)):
    await coment(data.get("id"),article_id, service,model)
    return {"message":"Se ha creado su comentario exitosamente"}



@router_users.post("/forgot_password", response_model=schemas.MsgResponse, summary="Ruta para obtener un token para recuperar la contraseña", status_code=status.HTTP_200_OK )
async def password_recovery(email:EmailStr=Body(...), repo:SqlAlchemyUserRepo=Depends(get_users_repo)):
    user=await repo.get_by_email_or_id(email=email)
    if not user:
        raise HTTPException(status_code=404, detail="No existe es email")
    token=await repo.create_otp(user.id)
    await send_email("Código para recuperación de contraseña", email, "Articles", f"Aquí tiene su token para recuperar la contraseña: {token.code}")
    return {"message":f"Hemos enviado un email con un código de recuperación al email {email}, tiene una fecha de expiración de 5 minutos"}


@router_users.post("/verify_token",response_model=schemas.MsgResponse, summary="Ruta para verificar el token", status_code=status.HTTP_200_OK )
async def verify(response:Response,code:int=Body(...), repo:SqlAlchemyUserRepo=Depends(get_users_repo)):
    user_id=await verify_otp(code, repo)
    response.set_cookie(
        key="otp_user_id",
        value=str(user_id),
        httponly=True,  
        max_age=300,    
        secure=True,    
        samesite="Strict"
    )
    return {"message":"Código verificado"}



@router_users.post("/new_password", response_model=schemas.MsgResponse, status_code=status.HTTP_200_OK)
async def reset_password(request: Request, model:user_schemas.NewPassword, repo: SqlAlchemyUserRepo = Depends(get_users_repo)):
    user_id = request.cookies.get("otp_user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Sesión no válida o cookie expirada")


    user=await repo.get_by_email_or_id(id=user_id)
    user.password=hash_password(model.password)
    await repo.commit_()

    return {"message": "Contraseña actualizada exitosamente"}


@router_users.post("/like/{article_id}", response_model=schemas.MsgResponse, status_code=status.HTTP_200_OK)
async def to_like(article_id:int, repo:SqlalchemyArticleRepo=Depends(get_repo), data=Depends(get_current_user)):
    like=await react(article_id, data.get("id"),repo)
    return like



@router_users.put("/add_to_favorite/{article_id}", response_model=schemas.MsgResponse, status_code=status.HTTP_200_OK)
async def add_favorite(article_id:int, repo:SqlalchemyArticleRepo=Depends(get_repo), data=Depends(get_current_user)):
    return await add_to_favorites(article_id, repo)


@router_users.get("/get_favorites/", response_model=List[schemas.ArticleList], status_code=status.HTTP_200_OK)
async def get_favoritess(repo:SqlalchemyArticleRepo=Depends(get_repo), data=Depends(get_current_user)):
    return await repo.get_favorites()