# UrbanFootprint Local Installation for MS Windows

UrbanFootprint is designed for Unix-like systems and cannot run natively run on Windows. But, we **can** use VirtualBox to run a Linux virtual machine
on a Windows computer. This requires a slightly different configuration than the standard installation instructions.

One major caveat is that, at present, we do not support mounting the UF git repository into VagrantBox using the "shared folders" feature because of
VirtualBox's inconsistent support for filesystem symbolic links across the range of Windows versions. For this reason, we manage all UF files directly
in the virtual machine and these files are not "visible" to Windows directly.

### Windows Prerequisites - Install all in Windows

* [Download and install VirtualBox](https://www.virtualbox.org/wiki/Downloads) -- VirtualBox allows us to create a Linux Virtual Machine on your Windows computer
* [Download and install Vagrant](https://www.vagrantup.com/downloads.html) -- A command line tool for interacting with VirtualBox and building the UF virtual machine
* [Download and install Git-bash for Windows](https://git-scm.com/download/win) -- A quick way to get a bash prompt on Windows

## First-time VM configuration

The "host" computer is the machine running VirtualBox. The "guest" machine is the virtual machine running within VirtualBox.

After installing [Git-Bash](https://git-scm.com/download/win) you should find a "Git Bash" icon in your Start Menu. Open "Git Bash" and you
should see a command prompt for the **host** computer:

    wget -O Vagrantfile https://raw.githubusercontent.com/CalthorpeAnalytics/urbanfootprint/master/Vagrantfile-windows
    vagrant up
    vagrant ssh

## Quickstart

This version imports a pre-built database to get you up and running quickly. It runs all services in "production"
mode which is suitable for test-driving the application, but not for doing active software development. We recommend
you start with this approach.

After you have run `vagrant ssh` and have a command prompt inside the **guest** VM that includes `/srv/calthorpe/urbanfootprint` run the following commands:

    ./quickstart.sh

When that has completed you can open [http://localhost:3333/footprint/](http://localhost:3333/footprint/) in your browser. The default
username is "admin@urbanfootprint.net" and the default password is "admin@uf".

**If you're following the "Quickstart" path you can stop here and [start using UF in your browser!](http://localhost:3333/footprint/)**

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
