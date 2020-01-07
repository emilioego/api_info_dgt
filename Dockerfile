# Dockerfile - This a Dockerfile for API Puntos DGT
FROM python:3.8
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app/app.py"]