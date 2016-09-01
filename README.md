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

Interested in installing UrbanFootprint on your own computer? Detailed installation instructions
are available for Mac OS X and MS Windows:

* Mac OS X -- [README-developers.md](README-developers.md)
* MS Windows -- [README-developers-windows.md](README-developers-windows.md)

# UrbanFootprint Client Configuration

Each UrbanFootprint installation needs a client configuration which is specific to the geographic
region being studied. UrbanFootprint client configurations reside in their own standalone git repository
that is referenced in UrbanFootprint as a [git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules).

We provide sample client configurations in the [urbanfootprint-configuration repository](https://github.com/CalthorpeAnalytics/urbanfootprint-configuration).
The recommended way to manage client configurations is to [fork](https://help.github.com/articles/fork-a-repo/) the
[urbanfootprint-configuration](https://github.com/CalthorpeAnalytics/urbanfootprint-configuration) repo. You can
then model a new client configuration off of the existing clients.

Copyright (C) 2016 [Calthorpe Analytics](http://calthorpeanalytics.com/)
