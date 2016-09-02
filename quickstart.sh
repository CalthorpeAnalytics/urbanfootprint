#!/bin/bash -e

echo ""
echo "********************************************************************"
echo "********************************************************************"
echo ""
echo "  UrbanFootprint quickstart process is starting ..."
echo ""
echo "********************************************************************"
echo "********************************************************************"
echo ""

# working directory for all UF command
cd /srv/calthorpe/urbanfootprint

# stop all services
sudo supervisorctl stop all
sudo service supervisor stop
sudo service postgresql restart

# install python dependencies
pip install -r requirements.txt

# copy sample environment settings for default configuration
cp .env.sample .env

# retrieve sample web database
wget -O urbanfootprint-sacog-web-db.sql.gz https://s3-us-west-2.amazonaws.com/uf-provisioning/urbanfootprint-sacog-web-db.sql.gz
gunzip -f urbanfootprint-sacog-web-db.sql.gz

# import sample web database
psql -U postgres -c "DROP DATABASE IF EXISTS urbanfootprint;"
psql -U postgres -c "CREATE DATABASE urbanfootprint;"
psql -U postgres -c "GRANT ALL ON DATABASE urbanfootprint TO calthorpe;"
psql -U postgres urbanfootprint < urbanfootprint-sacog-web-db.sql

# finish installation and deployment process
fab -f footprint/installer localhost quickstart

echo ""
echo "********************************************************************"
echo "********************************************************************"
echo ""
echo "  UrbanFootprint quickstart is complete. Open your web browser to:"
echo "    http://localhost:3333/footprint/"
echo "  using the following default credentials:"
echo "    user: admin@urbanfootprint.net"
echo "    pass: admin@uf"
echo ""
echo "********************************************************************"
echo "********************************************************************"
echo ""

exit 0
