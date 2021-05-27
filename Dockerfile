FROM python:3.7-slim

ARG HOST=localhost
ARG USER=guest
ARG PASS=guest
ARG PORT=5672
ARG MNG_PORT=15672
ARG TIME=10

COPY /src /sourceSeparation

WORKDIR /sourceSeparation

ADD https://github.com/deezer/spleeter/releases/download/v1.4.0/2stems.tar.gz 2stems.tar.gz 

RUN tar -xzf 2stems.tar.gz && rm 2stems.tar.gz && \
    apt-get update && apt-get install curl -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    mkdir /Audios && mkdir /Separation && \
    pip install --no-cache-dir -r ./requirements.txt && \
    chmod +x ./wait-for-rabbit.sh

ENTRYPOINT ["./wait-for-rabbit.sh", "python", "separate.py"]