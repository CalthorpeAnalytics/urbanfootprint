# Building Debs for UrbanFootprint Provisioning

UrbanFootprint provisioning require several packages to be compiled from source.
This is a time consuming process and is not desirable to do every time you
provision a developer or production instance. The scripts in this directory use
[Docker](http://docker.com) and [FPM](https://github.com/jordansissel/fpm) to
compile code from source and then save them as Debian packages. The Debian
packages are then installed via Ansible in
`provisioning/roles/web/tasks/geo.yml`.

## To run using Docker:

    ./build-in-docker.sh

## This produces the following files:

    uf-gdal_1.10.1_amd64.deb
    uf-geos_3.4.2_amd64.deb
    uf-proj_4.8.0_amd64.deb

## To place updated version of these files on S3 run something like:

    aws s3 cp uf-gdal_1.10.1_amd64.deb s3://uf-provisioning/
    aws s3 cp uf-geos_3.4.2_amd64.deb  s3://uf-provisioning/
    aws s3 cp uf-proj_4.8.0_amd64.deb  s3://uf-provisioning/
