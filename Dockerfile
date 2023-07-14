FROM public.ecr.aws/docker/library/python:3.11.5-slim

RUN apt-get update && apt-get install make
RUN apt-get install -y python3-setuptools groff

RUN pip3 install "poetry"
RUN pip3 --no-cache-dir install --upgrade awscli

ENV WORK_DIR="/var/task"
WORKDIR ${WORK_DIR}

COPY poetry.lock pyproject.toml README.md .env Makefile ${WORK_DIR}/

COPY geospatial_agent ${WORK_DIR}/geospatial_agent
COPY tests ${WORK_DIR}/tests

RUN poetry install
ADD data ${WORK_DIR}/data
