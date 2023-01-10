#!/bin/bash

# Get the CI_REGISTRY_IMAGE variable
source .env

# Build docker images
docker push $CI_REGISTRY_IMAGE/python_base:latest
docker push $CI_REGISTRY_IMAGE/data_sim:latest
docker push $CI_REGISTRY_IMAGE/pipeline:latest
docker push $CI_REGISTRY_IMAGE/data_store:latest
docker push $CI_REGISTRY_IMAGE/sidecar:latest
docker push $CI_REGISTRY_IMAGE/frontend:latest