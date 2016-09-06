# UrbanFootprint Cloud Installation

These are the recommended steps for getting up and running with a demo UrbanFootprint production instance on a cloud server.

## Prerequisites

You'll need:

* A dedicated server running [Ubuntu 14.04](https://wiki.ubuntu.com/TrustyTahr/ReleaseNotes) that you have ssh access to. On AWS, we recommend *"Ubuntu Server 14.04 LTS (HVM), SSD Volume Type"*
* A user account with root privileges (usually via sudo).

We recommend at least 2 CPUs and 8GB of RAM. On AWS, select t2.large or larger [instance type](https://aws.amazon.com/ec2/instance-types/).

## Installation

We provide a "quickstart" script that handles installing all dependencies and pre-loads a sample data set.

	wget https://raw.githubusercontent.com/CalthorpeAnalytics/urbanfootprint/master/quickstart.sh
	chmod +x quickstart.sh
	sudo ./quickstart.sh
	
Expect this script to take 15-20 minutes to complete. You'll know it's done when you see something like this:

	********************************************************************
	********************************************************************
	
	  UrbanFootprint quickstart is complete. Open your web browser to:
	    http://<YOUR-IP-HERE>/
	  using the following default credentials:
	    user: admin@urbanfootprint.net
	    pass: admin@uf
	
	********************************************************************
	********************************************************************


# Using UF

## Login with the default login

The quickstart script will attempt to detect the public IP address of the server and print out a URL to use. If that doesn't work, determine the server's IP address using your cloud provider's tools and put the IP address in your web browser's location bar.

When you first access your UF instance, you will be directed to the login page.
Login credentials are the following:

>username: `admin@urbanfootprint.net`

>password: `admin@uf`

For information on how to create new users, please reference the
[User Manager](http://urbanfootprint-v1.readthedocs.io/en/latest/user_manager/) section of the documentation.

## User Guide

[http://urbanfootprint-v1.readthedocs.io/en/latest/](http://urbanfootprint-v1.readthedocs.io/en/latest/)

Copyright (C) 2016 [Calthorpe Analytics](http://calthorpeanalytics.com/)
