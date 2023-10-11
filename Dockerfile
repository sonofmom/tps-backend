FROM python:3.10-bullseye

ADD requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

WORKDIR /app
ADD backend/ /app/backend
