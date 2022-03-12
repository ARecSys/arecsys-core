FROM python:3.8

WORKDIR /src

COPY requirements.txt requirements.txt

COPY /src/ /src/

RUN pip install -r requirements.txt

EXPOSE 6000

ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:6000", "--timeout", "600", "app:app" ]
