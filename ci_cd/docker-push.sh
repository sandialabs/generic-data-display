#!/bin/bash
source ./docker.config

docker push ${IMAGE_NAME}:latest
