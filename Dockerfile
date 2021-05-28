FROM python:3.7-slim

ARG HOST=localhost
ARG USER=guest
ARG PASS=guest
ARG PORT=5672
ARG MNG_PORT=15672
ARG TIME=10

COPY /src /sourceSeparation

WORKDIR /sourceSeparation

RUN apt-get update && apt-get install curl libsndfile1 ffmpeg -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r ./requirements.txt && \
    chmod +x ./wait-for-rabbit.sh

ENTRYPOINT ["./wait-for-rabbit.sh", "python", "separate.py"]