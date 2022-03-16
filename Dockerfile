FROM python:3.8

WORKDIR /src

COPY requirements.txt requirements.txt

COPY /src/ /src/

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "app.py" ]
