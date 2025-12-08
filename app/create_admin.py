from app.database.models import User, Writer, Admin
from app.database.database import AsyncLocalSession
from typing import Literal

from sqlalchemy import select
import asyncio
from app.utils import hash_password


UserType=Literal["admin","writer"]
#No vamos a hashear la contraseña ni a verificar que no haya emails repetidos ya que es solo para pruebas
async def createadmin(password,firstname="John", lastname="Doe", email="userexample@gmail.com", user_type:UserType="admin"):

    async with AsyncLocalSession() as session:
        stmt=select(User).where(User.email==email)
        result=await session.execute(stmt)
        existing_email=result.scalar_one_or_none()
        if existing_email:
            raise ValueError("Ya existe una cuenta con ese email , introduce otro")
        if user_type not in ["admin", "writer"]:
            raise ValueError(f"El tipo de usuario solo puede ser writer o admin")
        class_=Writer if user_type=="writer" else Admin
        admin=class_(
        firstname=firstname,
        lastname=lastname,
        email=email,
        password=hash_password(password),
        user_type=user_type
    )
        session.add(admin)
        await session.commit()

    return f"Usuario creado correctamente"


async def main():
    print("Crea un usuario admin o writer para consumir endpoints")

    firstname=str(input("Primer nombre (John por defecto): ")) or "John"
    lastname=str(input("Escribe tus apellidos (Doe por defecto)")) or "Doe"
    email=str(input("Email para pruebas (userexample@gmail.com por defecto) pero si quieres recibir correctamente los mensajes que envian ciertos endpoints, introduce uno real: ")) or "userexample@gmail.com"
    password=str(input("Tu contraseña, no la olvides: ")) or None
    user_type=str(input("Introduce el rol de usuario que deseas: writer o admin , en minúsculas todo: "))

    if not password:
        raise ValueError("La contraseña es obligatoria: ")
    

    if await createadmin(password,firstname,lastname,email,user_type):
        print("Ha creado su usuario exitosamente")

    else:
        print("No se ha podido crear su usuario")
if __name__ == "__main__":
    asyncio.run(main())