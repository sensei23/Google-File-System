FROM python:3.7.8-slim

COPY master_server/requirements/common.txt requirements/common.txt
RUN pip install -U pip && pip install -r requirements/common.txt

COPY ./master_server/api /app/api
COPY ./master_server/bin /app/bin
COPY ./models /app/models
# COPY ./logging /app/logging
COPY ./utils /app/utils
COPY ./master_server/wsgi.py /app/wsgi.py
COPY ./master_server/config /app/config
WORKDIR /app

EXPOSE 5000

# ENTRYPOINT ["bash", "/app/bin/run.sh"]
#run without gunicorn
ENTRYPOINT ["python", "-u","/app/wsgi.py"]
