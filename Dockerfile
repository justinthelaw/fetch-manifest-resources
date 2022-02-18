ARG BASE_REGISTRY=registry1.dso.mil
ARG BASE_IMAGE=ironbank/opensource/python/python39
ARG BASE_TAG=v3.9.10

FROM ${BASE_REGISTRY}/${BASE_IMAGE}:${BASE_TAG}

WORKDIR /app

COPY ./ /app

RUN pip install -r requirements.txt

WORKDIR /work

ENTRYPOINT [ "/usr/local/bin/python", "/app/fetch.py" ]