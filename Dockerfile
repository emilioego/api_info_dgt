# Dockerfile - This a Dockerfile for API Puntos DGT

FROM python:3.8.1

LABEL Author="Emilio Garcia & Lucia Falcon"
LABEL E-mail="emilioego@hotmail.com;lucfalgar@gmail.com"
LABEL version="1.0"

ENV PYTHONDONTWRITEBYTECODE 1
ENV FLASK_APP "app/app.py"
ENV FLASK_ENV "development"
ENV FLASK_DEBUG False

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]

EXPOSE 5000

CMD flask run --host=0.0.0.0