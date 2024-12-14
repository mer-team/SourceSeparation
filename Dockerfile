ARG BASE_VERSION=2.4.0-stems-local

FROM mer-team/spleeter:${BASE_VERSION}

ARG HOST=localhost
ARG USER=guest
ARG PASS=guest
ARG PORT=5672
ARG MNG_PORT=15672
ARG TIME=10

# copy first requirements to cache pip install layer
COPY /src/requirements.txt /sourceSeparation/
WORKDIR /sourceSeparation

RUN pip install --no-cache-dir -r ./requirements.txt

# this layer changes frequently during dev builds
COPY /src /sourceSeparation
RUN chmod +x ./wait-for-rabbit.sh

ENTRYPOINT ["./wait-for-rabbit.sh", "python", "separate.py"]