FROM python:3.11-slim

WORKDIR /app


COPY requirements.txt ./


RUN pip install --no-cache-dir -r requirements.txt


COPY . .


RUN mkdir -p instance


ENV FLASK_APP=CNC_szamolo/app.py
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5000


CMD ["flask", "run"]