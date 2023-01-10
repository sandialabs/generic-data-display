#!/bin/bash

# Build python backend
python3 -m venv .venv
.venv/bin/python3 setup.py bdist_wheel

# Get the CI_REGISTRY_IMAGE variable
source .env

# Build docker images
docker build -f Dockerfile.python_base --build-arg CI_REGISTRY_IMAGE=$CI_REGISTRY_IMAGE -t $CI_REGISTRY_IMAGE/python_base:latest --no-cache .
docker build -f Dockerfile.data_sim --build-arg CI_REGISTRY_IMAGE=$CI_REGISTRY_IMAGE -t $CI_REGISTRY_IMAGE/data_sim:latest --no-cache .
docker build -f Dockerfile.pipeline --build-arg CI_REGISTRY_IMAGE=$CI_REGISTRY_IMAGE -t $CI_REGISTRY_IMAGE/pipeline:latest --no-cache .
docker build -f Dockerfile.data_store --build-arg CI_REGISTRY_IMAGE=$CI_REGISTRY_IMAGE -t $CI_REGISTRY_IMAGE/data_store:latest --no-cache .
docker build -f Dockerfile.sidecar --build-arg CI_REGISTRY_IMAGE=$CI_REGISTRY_IMAGE -t $CI_REGISTRY_IMAGE/sidecar:latest --no-cache .
docker build -f Dockerfile.frontend --build-arg CI_REGISTRY_IMAGE=$CI_REGISTRY_IMAGE -t $CI_REGISTRY_IMAGE/frontend:latest --no-cache .