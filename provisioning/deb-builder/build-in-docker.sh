#!/bin/bash

# This script creates a Docker image with dependencies necessary
# for compiling a number of geospatial libraries that UrbanFootprint
# depends on. It then uses the Docker image to run build-debs.sh to
# compile and produce debian packages for the geospatial libraries.
# This saves each UF instance from having to compile these libraries
# from source and instead just get a binary installation.

docker build -t uf-deb-builder .

docker run --rm -v "$(pwd):/code" uf-deb-builder /code/build-debs.sh
