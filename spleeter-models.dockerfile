ARG BASE_VERSION=2.4.0-local

FROM mer-team/spleeter:${BASE_VERSION}

ARG MODEL_VERSION=1.4.0
ARG TWO_STEMS=true
ARG FOUR_STEMS=true
ARG FIVE_STEMS=true

ENV MODEL_PATH /model

ARG MODEL=2stems
RUN if [ "$TWO_STEMS" = "true" ]; then \
        mkdir -p /model/$MODEL && \
        curl -fsSL https://github.com/deezer/spleeter/releases/download/v$MODEL_VERSION/$MODEL.tar.gz -o /tmp/$MODEL.tar.gz && \
        tar -xvzf /tmp/$MODEL.tar.gz -C /model/$MODEL/ && \
        touch /model/$MODEL/.probe && \
        rm /tmp/$MODEL.tar.gz \
    ; fi

ARG MODEL=4stems
RUN if [ "$FOUR_STEMS" = "true" ]; then \
        mkdir -p /model/$MODEL && \
        curl -fsSL https://github.com/deezer/spleeter/releases/download/v$MODEL_VERSION/$MODEL.tar.gz -o /tmp/$MODEL.tar.gz && \
        tar -xvzf /tmp/$MODEL.tar.gz -C /model/$MODEL/ && \
        touch /model/$MODEL/.probe && \
        rm /tmp/$MODEL.tar.gz \
    ; fi

ARG MODEL=5stems
RUN if [ "$FIVE_STEMS" = "true" ]; then \
        mkdir -p /model/$MODEL && \
        curl -fsSL https://github.com/deezer/spleeter/releases/download/v$MODEL_VERSION/$MODEL.tar.gz -o /tmp/$MODEL.tar.gz && \
        tar -xvzf /tmp/$MODEL.tar.gz -C /model/$MODEL/ && \
        touch /model/$MODEL/.probe && \
        rm /tmp/$MODEL.tar.gz \
    ; fi