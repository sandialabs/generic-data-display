#!/bin/bash
source ./docker.config

# Grab our conda env config so the container works
cp ../gd2-conda-environment.yml .

docker build -t ${IMAGE_NAME}:latest \
    --build-arg CI_REGISTRY=${CI_REGISTRY} \
    .

rm gd2-conda-environment.yml