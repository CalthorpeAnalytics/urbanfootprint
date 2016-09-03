# UrbanFootprint Local Installation

These are the recommended steps for installing and running a local UrbanFootprint development environment on a computer running Mac OS X or MS Windows.

## Prerequisites

### Mac Prerequisites - Install all in Mac OS X or Linux Desktop

* [Download and install VirtualBox](https://www.virtualbox.org/wiki/Downloads) -- VirtualBox allows us to create a Linux Virtual Machine
* [Download and install Vagrant](https://www.vagrantup.com/downloads.html) -- A command line tool for interacting with VirtualBox and building the UF virtual machine

### Windows Prerequisites - Install all in Windows

* [Download and install VirtualBox](https://www.virtualbox.org/wiki/Downloads) -- VirtualBox allows us to create a Linux Virtual Machine on your Windows computer
* [Download and install Vagrant](https://www.vagrantup.com/downloads.html) -- A command line tool for interacting with VirtualBox and building the UF virtual machine
* [Download and install Git-bash for Windows](https://git-scm.com/download/win) -- A quick way to get a bash prompt on Windows

*NOTE: In order to use VirtualBox v5.1.x (on Windows or Mac) you must to install Vagrant 1.8.5+. For older versions of Vagrant make sure to install [VirtualBox version 5.0.x](https://www.virtualbox.org/wiki/Download_Old_Builds_5_0), which is available from the [VirtualBox Old Builds](https://www.virtualbox.org/wiki/Download_Old_Builds).*

## Developer VM Configuration

This version installs and configures a full developer environment. It runs all services in "development" mode,
which is slower and more resource intensive than "production" mode. We recommend running in this mode once you
are ready to dive into Python and JavaScript development for UrbanFootprint.

For reference, the "host" computer is the machine running VirtualBox (your Mac or Windows computer). The "guest" machine is the virtual machine running within VirtualBox.

Run the following commands on the **host** computer:

    git clone https://github.com/CalthorpeAnalytics/urbanfootprint.git urbanfootprint
    git clone https://github.com/CalthorpeAnalytics/urbanfootprint-configuration.git urbanfootprint-configuration
    cd urbanfootprint
    git submodule init
    git submodule update
    vagrant up
    vagrant ssh

You will now be ssh'd into the guest VM and should have a Linux command prompt in the `/srv/calthorpe/urbanfootprint` directory.

    cp .env.sample .env
    wget https://s3-us-west-2.amazonaws.com/uf-provisioning/urbanfootprint-sacog-source-db.sql.gz
    gunzip urbanfootprint-sacog-source-db.sql.gz
    psql -U postgres -c "DROP DATABASE IF EXISTS urbanfootprint_sacog_source;"
    psql -U postgres -c "CREATE DATABASE urbanfootprint_sacog_source;"
    psql -U postgres urbanfootprint_sacog_source < urbanfootprint-sacog-source-db.sql

    pip install -r requirements.txt
    fab -f footprint/installer localhost build:dev
    fab -f footprint/installer localhost restart_dev

## Running UF in Developer Mode

## To run all services on the VM (RECOMMENDED)

All developer services are managed by supervisor. The easiest way to make sure everything is up and running is this:

    fab -f footprint/installer localhost restart_dev
    
NOTE: After every VM reboot (via a vagrant reload or otherwise) *YOU MUST* run `fab -f footprint/installer localhost restart_dev`    

If you want to see what commands are being run by supervisor, look in `conf/etc/supervisor/conf.d/calthorpe.supervisor.dev`

#### Access your UF instance in a browser from your workstation

[http://localhost:3333/fp/](http://localhost:3333/fp/)

## OPTIONAL (Mac Only): Run Nginx + Sproutcore on the Host Machine

The sproutcore server is faster when served up from your local Mac, but the Django server must be run on the VM.

#### Install and configure rbenv on your Mac

You only have to do this once.

    cd ~/src/urbanfootprint
    git pull
    CONFIGURE_OPTS=--with-openssl-dir=`brew --prefix openssl` rbenv install 1.9.3-p551

#### Add this line to your .bashrc:

    eval "$(rbenv init -)"

#### Install bundle and set up:

This will install gems to your local rbenv.

    eval "$(rbenv init -)"
    gem install bundler
    bundle config build.eventmachine --with-cppflags=-I`brew --prefix openssl`/include
    bundle install

#### Install and configure nginx on the Mac:

    brew install nginx
    rm /usr/local/etc/nginx/nginx.conf
    sudo mkdir /var/log/nginx
    sudo touch /var/log/nginx/uf_dev.log
    ln -s `pwd`/conf/etc/nginx/sites-available/calthorpe.nginx.osx /usr/local/etc/nginx/nginx.conf

#### Start services

Once the above setup is done, this is how you run the services on your Mac:

##### nginx

    sudo nginx

##### sproutcore

    cd sproutcore
    sproutcore server

#### Access UF instance from your Mac:

[http://localhost:8080/fp/](http://localhost:8080/fp/)


## Using UF

## Login with the default login:

When you first access your UF instance, you will be directed to the login page.
Login credentials are the following:

>username: `admin@urbanfootprint.net`

>password: `admin@uf`

For information on how to create new users, please reference the
[User Manager](http://urbanfootprint-v1.readthedocs.io/en/latest/user_manager/) section of the documentation.


## User Guide

[http://urbanfootprint-v1.readthedocs.io/en/latest/](http://urbanfootprint-v1.readthedocs.io/en/latest/)

Copyright (C) 2016 [Calthorpe Analytics](http://calthorpeanalytics.com/)
