# !/bin/bash

# docker build -t wegold/ds553 .
docker buildx build --platform linux/amd64 -t wegold/ds553 . 
docker push wegold/ds553