FROM python:alpine

RUN apk add --no-cache tzdata
ENV TZ=Europe/Amsterdam

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

CMD ["python", "-u", "run.py"]
