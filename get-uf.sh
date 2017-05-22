#!/bin/bash

set -e

# TODO:
#  - we could do some sanity checks here to make sure Vagrant and
#    Virtualbox are installed

echo ""
echo "********************************************************************"
echo "********************************************************************"
echo ""
echo "  UrbanFootprint quickstart process is starting ..."
echo ""
echo "********************************************************************"
echo "********************************************************************"
echo ""

# Download Vagrantfile
curl -# -o Vagrantfile https://raw.githubusercontent.com/CalthorpeAnalytics/urbanfootprint/master/Vagrantfile-prebuilt

# Start the VM using Vagrant
vagrant up

echo ""
echo "********************************************************************"
echo "********************************************************************"
echo ""
echo "  UrbanFootprint quickstart is complete. Open your web browser to:"
echo "    http://localhost:3333/footprint/"
echo ""
echo "  using the following default credentials:"
echo "    user: admin@urbanfootprint.net"
echo "    pass: admin@uf"
echo ""
echo "********************************************************************"
echo "********************************************************************"
echo ""

exit 0
