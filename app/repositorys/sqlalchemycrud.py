from sqlalchemy import select
from sqlalchemy.orm import selectinload, selectin_polymorphic

from app.database.models import User, Writer, Admin,OTP
from sqlalchemy.ext.asyncio import AsyncSession
from random import randint


class SqlAlchemyUserRepo():
    def __init__(self, session:AsyncSession):
        self.session=session

    async def commit_(self):
        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"No se ha podido hacer commit, error :{str(e)}")
        
    async def commit_and_refresh(self, obj):
        if obj is None:
            raise ValueError("Debe pasar un obj para hacer commit")
        try:
            await self.session.commit()
            await self.session.refresh(obj)
            return obj
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"No se ha podido actualizar el objeto, error :{str(e)}")

    #Función para guardar un objeto usuario
    async def save(self, obj_user):
        try:
            self.session.add(obj_user)
            await self.session.commit()
            await self.session.refresh(obj_user)
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"No se ha podido guardar el objeto, error :{str(e)}")
        return obj_user
    
    #Función para obtener un usuario por su id o por su email
    async def get_by_email_or_id(self,email:str=None,id:int=None):
    
    #Comprobamos que no recibimos ambos parámetros
        if email and id:
            raise ValueError("Solo puedes introducir uno entre email y id")
        #Aplicamos la lógica según lo recibido
        if email:
            stmt=select(User).options(selectin_polymorphic(User,[Writer, Admin]),
                                selectinload(Writer.articles)).where(User.email==email)
        if id:
            stmt=select(User).options(selectin_polymorphic(User,[Writer, Admin]),
                                selectinload(Writer.articles)).where(User.id==id)
        result=await self.session.execute(stmt)
        user=result.scalar_one_or_none()
        return user
        
    
    #Función para obtener a todos los usuarios usando paginación por cursor
    async def get_all(self,cursor:int=0):
        #Hacemos la consulta para obtener a todos los usuarios, con id mayor que el cursor 
        stmt=select(User).where(User.id>cursor).order_by(User.id).limit(15)
        result=await self.session.execute(stmt)
        users=result.scalars().all()
        #Obtenemos el id del último objeto usuario
        next_cursor=None
        if users:
            last_user=users[-1]

        #Esta será la variable que informará al consumidor de la API, por cuál objeto se quedó
            next_cursor=last_user.id if len(users)==15 else None
        #Si la longitud de los resultados de la query es menor a 15, significa que no hay mas objetos y por ende no hay próximo cursor y has_more es Falso
        
        has_more=len(users)==15

        return{
            "next_cursor":next_cursor,
            "has_more":has_more,

            "items":users
        }

    #Función para eliminar
    async def delete(self, user_id:int):
        user=await self.get_by_email_or_id(id=user_id)
        if user:
            await self.session.delete(user)
            await self.session.commit()

            return True
        return False

#Función para crear el otp que será enviado al usuario que olvide su contraseña
    async def create_otp(self,user_id:int):
        otp=OTP(
        code=randint(100000,999999),
        user_id=user_id
    )
        token=await self.save(otp)
        return token

#Función para obtener un otp por su código
    async def get_otp(self,code:int):
        stmt=select(OTP).where(OTP.code==code)
        result=await self.session.execute(stmt)
        otp=result.scalar_one_or_none()
        return otp