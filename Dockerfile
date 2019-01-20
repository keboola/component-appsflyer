FROM quay.io/keboola/docker-custom-python:latest
ENV PYTHONIOENCODING utf-8

COPY . /code/
## COPY /data/ /data/

RUN pip install flake8
RUN pip install dateparser

RUN pip install -r /code/requirements.txt

WORKDIR /code/


CMD ["python", "-u", "/code/src/main.py"]
