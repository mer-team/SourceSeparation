ARG PYTHON_VERSION=3.10

FROM python:${PYTHON_VERSION}-slim

ENV MODEL_PATH /model

RUN apt-get update && apt-get install curl libsndfile1 ffmpeg -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    mkdir -p /model 

ARG SPLEETER_VERSION=2.4.0

RUN pip install --no-cache-dir "spleeter==${SPLEETER_VERSION}"

ENTRYPOINT ["spleeter"]