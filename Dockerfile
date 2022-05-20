FROM python:3.6

WORKDIR /code

RUN pip install scipy scikit-learn==0.19.1 fastapi uvicorn databases pandas asyncpg 

COPY . /code/

EXPOSE 8000

CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]