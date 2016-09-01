# See README.md in this directory for more information.
FROM ruby:2.3

RUN mkdir -p /code
WORKDIR /code

# FPM dependencies
# https://github.com/jordansissel/fpm
RUN apt-get update && apt-get install -y \
      npm \
      php-pear \
      python-setuptools \
      rpm \
    && rm -rf /var/lib/apt/lists/*

RUN gem install fpm

# UF compilation dependencies
RUN apt-get update && apt-get install -y \
      build-essential \
      curl \
      curl \
      gdal-bin \
      git \
      libevent-dev \
      libfreetype6-dev \
      libgdal1-dev \
      libproj-dev \
      python \
      python-dev \
      python-gdal \
      python-pip \
      sudo \
    && rm -rf /var/lib/apt/lists/*
