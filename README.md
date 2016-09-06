# UrbanFootprint

UrbanFootprint 1.5 is a web-based, open source, scenario planning platform. It serves as a land use
planning, modeling, and data organization framework and is designed to facilitate more informed land
use and scenario planning. UrbanFootprint version 1.5 is built upon a suite of open source software
products and includes a set of web-based scenario development, editing, and analysis features. It is
available under a [GNU GPLv3 license](LICENSE.txt). UrbanFootprint’s development is led by Berkeley,
California-based Calthorpe Analytics.

A user guide for version 1.5 is at [http://urbanfootprint-v1.readthedocs.io/](http://urbanfootprint-v1.readthedocs.io/)

UrbanFootprint is developed by [Calthorpe Analytics](http://calthorpeanalytics.com/).

# UrbanFootprint Installation

Interested in installing UrbanFootprint on your own computer?

---

# UF Quickstart Cloud

To run a version of UrbanFootprint on your own server (such as an AWS EC2 instance), follow the instructions in **[README-cloud.md](README-cloud.md)**.

# UF Quickstart Local - Use a Pre-built VM

The fastest way to get up and running with a local UrbanFootprint installation is by using a pre-built
virtual machine.

### Quickstart Prerequisites for Mac OS X and MS Windows:

* [Download and install VirtualBox](https://www.virtualbox.org/wiki/Downloads) -- VirtualBox allows us to create a Linux Virtual Machine
* [Download and install Vagrant](https://www.vagrantup.com/downloads.html) -- A command line tool for interacting with VirtualBox and building the UF virtual machine
* [Download and install Git-bash _(Windows only)_](https://git-scm.com/download/win) -- A quick way to get a bash prompt on Windows

### Use Vagrant to bring up an UrbanFootprint VM

On Windows, open up "Git Bash" which should now be available in your Start Menu. On Mac, open up the Terminal app. You should now have a command line prompt. In the terminal, run:

    curl https://raw.githubusercontent.com/CalthorpeAnalytics/urbanfootprint/master/get-uf.sh | bash

A local UrbanFootprint instance is now accessible via  [http://localhost:3333/footprint/](http://localhost:3333/footprint/) in your browser. The default username is "admin@urbanfootprint.net" and the default password is "admin@uf".

**If you're following the "Quickstart" path you can stop here and [start using UF in your browser!](http://localhost:3333/footprint/)**

---

# UF Development Environment Installation

If you're looking to do active code development on the UrbanFootprint code base, then you'll need to
install a development environment. Detailed installation instructions are available for Mac OS X
and MS Windows in **[README-developers.md](README-developers.md)**

# UrbanFootprint Client Configuration

Each UrbanFootprint installation needs a client configuration which is specific to the geographic
region being studied. UrbanFootprint client configurations reside in their own standalone git repository
that is referenced in UrbanFootprint as a [git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules).

We provide sample client configurations in the [urbanfootprint-configuration repository](https://github.com/CalthorpeAnalytics/urbanfootprint-configuration).
The recommended way to manage client configurations is to [fork](https://help.github.com/articles/fork-a-repo/) the
[urbanfootprint-configuration](https://github.com/CalthorpeAnalytics/urbanfootprint-configuration) repo. You can
then model a new client configuration off of the existing clients.

Copyright (C) 2016 [Calthorpe Analytics](http://calthorpeanalytics.com/)
