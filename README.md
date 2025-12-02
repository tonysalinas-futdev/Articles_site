# API para web de artículos


## Teconologías utilizadas en el proyecto:
* Python
* Fastapi
* Postgresql
* Sqlalchemy
* Docker


 API desarrollada para que personas puedan leer y escribir artículos sobre temas que dominen o les parezcan interesantes, contiene:

* Todo un sistema de auteticación desarrollado por mí,utilizando JWT como estándar, hay endpoints para:
  * Crear una cuenta (puede ser de usuario , escritor o administrador)
   * Loguearse
   * Actualizar datos del perfil
   * Cambiar contraseña
   *  Recuperar la contraseña perdida mediante un OTP enviado por email
   *  Obtener un nuevo access_token utilizando el refresh
  
  * Permisos definidos según el tipo de usuario (user, admin, writer)
  * Programación asíncrona para manejar concurrencia


* Middleware para rate limiting usando slowapi
* Pydantic para las validaciones de tipo
* Validaciones de contraseña, nombres de usuario etc usando regex
* Tests unitarios y de integración para robustez utilizando pytest , pytest_ asyncio y pytest_cov para medir cobertura  
* Middleware de timeout usando asyncio
* Passlib para el hasheo de contraseñas
* python-jose para manjear la lógica de jwt

# Instrucciones para correr el proyecto
* 1- Crear un entorno virtual escribiendo en la consola:
  * `python venv -m nombre_del_entorno`

* 2- Activar el entorno virtual escribiendo en la consola:
  * `nombre_del_entorno/Scripts/activate`

* 3- Posicionarse en la carpeta principal (API_article), en cmd:
  * `cd API_article`

* 4- Establecer las variables de entorno, crear un archvio .env y fijarse en el .env.example.

* 5- Correr el servidor(puerto 8000 por defecto) con:
  *  `fastapi dev main.py`
  *  En caso de querer cambiar de puerto:
     *  `uvicorn main:app --port numero_de_puerto`
* 6- Para poder obtener la documentación con toda la info de las rutas solo debe abrir su navegador y pegar (luego de correr el servidor y si sigue usando el puerto 8000):
* `http://localhost:8000/docs` 

## Acceder a las rutas protegidas
Para poder acceder a las rutas protegidas , ya sea las de writer o admin simpemente debe escrbir en consola:

`python create_admin.py`

Ya con resto puede crearse una cuenta de admin o de writer y acceder a las rutas protegidas



## Para ejecutar los test:
Para ejecutar todos los test , debe escribir en consola:
* `pytest` (Para ejecutar todos los test).

* `pytest tests/archivo.py` (Para ejecutar un archivo en específico).
