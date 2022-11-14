FROM python:3.8
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /code/requirements.txt
COPY ..
WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
