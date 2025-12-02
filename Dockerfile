#Indicamos la imagen en la que se va a basar
FROM python:3.13-alpine

LABEL maintainer="kroosismo2020@gmail.com"

LABEL version="1.1.0"



COPY . /app

WORKDIR /app
RUN pip install -r requirements.txt
ENV PYTHONPATH=/app/app
EXPOSE 8000 

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]