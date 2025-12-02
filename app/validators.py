from pydantic import Field
import re
from fastapi import HTTPException
#Definimos fuciones para validar cada campo que lo necesite y así no repetimos código, el atributo required es para cuando no necesitemos que el camppo sea obligatorio

def password_validator(required=True):
    return Field(
        ... if required else None ,
        min_length=8,
        
        description="La contraseña debe tener una longitud minima de 8 caractéres y ademas incluir un símbolo especial entre @#$%&*+, una mayúscula y una minúscula ",
        

            )

def pattern_password_validation(valor):
    if not re.fullmatch(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[@#$%&*+])[a-zA-Z0-9@#$%&*+]{8,}$", valor):
        raise ValueError("La contraseña no cumple con los estándares")
    return valor


def name_validator(required=True):
    return Field(
        ... if required else None,
        max_length=40,
        min_length=2,
        description="Primer Nombre , nada de caracteres especiales , números o espacios antes o después del nombre",
        

)


