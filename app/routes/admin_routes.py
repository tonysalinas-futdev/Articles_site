from fastapi import APIRouter, Depends,status, HTTPException
from jwt_utils import get_current_user
from repositorys.sqlalchemy_tag_repo import SqlAlchemyTagRepo
from repositorys.sqlalchemycrud import SqlAlchemyUserRepo
import schemas
import user_schemas
from services.tags_service import create_tag, delete_tag
from dependences import  get_tag_repo,get_users_repo
from services.user_service import change_role
from send_email import send_email

router_admin=APIRouter(prefix="/admin", tags=["Admin"])


#Ruta para que el admin cree una etiqueta
@router_admin.post("/create_tag", response_model=schemas.TagBase, status_code=status.HTTP_200_OK)
async def create(model:schemas.CreateTag,repo:SqlAlchemyTagRepo=Depends(get_tag_repo),data=Depends(get_current_user)):
    if data.get("role")!="admin":
        raise HTTPException(status_code=401, detail="Usted no tiene autorización para acceder a esta ruta")
    return await create_tag(model,repo)
    


#Ruta para eliminar una etiqueta
@router_admin.delete("/delete/{tag_id}", response_model=schemas.MsgResponse, status_code=status.HTTP_200_OK )
async def delete_(tag_id:int, repo:SqlAlchemyTagRepo=Depends(get_tag_repo),data=Depends(get_current_user)):
    if data.get("role")!="admin":
        raise HTTPException(status_code=401, detail="Usted no tiene autorización para acceder a esta ruta")
    await delete_tag(tag_id,repo)
    return {"message":f"La etiqueta con id {tag_id} ha sido elminado correctamente"}



#Ruta para obtener la info de cualquier usuario
@router_admin.get("/get_user/{user_id}", response_model=user_schemas.UserBase, summary="Ruta del admin para obtener la información detallada de un usuario")
async def get_user(user_id: int,repo:SqlAlchemyUserRepo=Depends(get_users_repo),data=Depends(get_current_user)):
    if data.get("role")!="admin":
        raise HTTPException(status_code=401, detail="Usted no tiene autorización para acceder a esta ruta")
    user= await repo.get_by_email_or_id(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="No se ha encontrado ningún usuario con ese id")
    return user


#Ruta para obtener una lista con todos los usuarios
@router_admin.get("/get_all_users", response_model=user_schemas.GetAllPaginated, status_code=status.HTTP_200_OK)
async def get_all(cursor: int=0, repo:SqlAlchemyUserRepo=Depends(get_users_repo),data=Depends(get_current_user)):
    if data.get("role")!="admin":
        raise HTTPException(status_code=401, detail="Usted no tiene autorización para acceder a esta ruta")
    return await repo.get_all(cursor)



#Ruta para poder cambiar el rol de un usuario
@router_admin.put("/promote_user/{user_id}", response_model=schemas.MsgResponse, status_code=status.HTTP_200_OK, summary="Ruta para que el admin cambie el tipo de usuario de alguna cuenta")
async def promote(user_id:int, model:user_schemas.ChangeRole, repo:SqlAlchemyUserRepo=Depends(get_users_repo),data=Depends(get_current_user)):
    if data.get("role")!="admin":
        raise HTTPException(status_code=401, detail="Usted no tiene autorización para acceder a esta ruta")
    user=await change_role(user_id, model, repo)
    await send_email("Cambio de rol", user.email, "DevArticles",f"Le informamos mediante este correo que su rol de usuario ha cambiado a {user.user_type}")
    return {"message":f"Ha cambiado el rol del usuario {user.firstname} {user.lastname} exitosamente"}


#Ruta para que el admin pueda eliminar una cuenta
@router_admin.delete("/delete_account/{user_id}", response_model=schemas.MsgResponse, summary="Ruta para eliminar la cuenta de un usuario", status_code=status.HTTP_200_OK)
async def delete_acc(user_id:int , repo:SqlAlchemyUserRepo=Depends(get_users_repo),data=Depends(get_current_user)):
    if data.get("role")!="admin":
        raise HTTPException(status_code=401, detail="Usted no tiene autorización para acceder a esta ruta")
    if await repo.delete(user_id):
        return {"message":f"Se ha eliminado correctamente al usuario con id: {user_id}"}
    else:
        raise HTTPException(status_code=404, detail="No se ha podido eliminar al usuario , asegurese que ese id exista")
