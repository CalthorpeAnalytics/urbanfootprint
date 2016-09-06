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

apt-get update
apt-get install -y software-properties-common
apt-add-repository -y ppa:ansible/ansible-1.9
apt-get update
apt-get install -y ansible git
mkdir -p /srv/calthorpe/

# clone urbanfootprint repos
cd /srv/calthorpe/
git clone https://github.com/CalthorpeAnalytics/urbanfootprint.git urbanfootprint
git clone https://github.com/CalthorpeAnalytics/urbanfootprint-configuration.git urbanfootprint-configuration
cd /srv/calthorpe/urbanfootprint/
git submodule init
git submodule update

# run ansible provisioning
cd /srv/calthorpe/urbanfootprint/provisioning
ansible-galaxy install -f -r galaxy-roles.yml
ansible-playbook -v -i 'localhost', -c local site.yml

# let calthorpe user ssh in for fabric
su - calthorpe -c "ssh-keygen -f ~/.ssh/id_rsa -N ''"
su - calthorpe -c "ssh-keyscan -H localhost > ~/.ssh/known_hosts"
su - calthorpe -c "cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys"

# set file permissions
chown -R calthorpe:calthorpe /srv/calthorpe/urbanfootprint*

# stop all services
supervisorctl stop all
service supervisor stop
service postgresql restart

# install python dependencies (though really all we need is fabric as this point)
/srv/calthorpe_env/bin/pip install -r /srv/calthorpe/urbanfootprint/requirements.txt
chown -R calthorpe:calthorpe /srv/calthorpe_env

# copy sample environment settings for default configuration
cp /srv/calthorpe/urbanfootprint/.env.sample /srv/calthorpe/urbanfootprint/.env
chown calthorpe:calthorpe /srv/calthorpe/urbanfootprint/.env

# retrieve sample web database
wget -O /srv/datadump/urbanfootprint-sacog-web-db.sql.gz https://s3-us-west-2.amazonaws.com/uf-provisioning/urbanfootprint-sacog-web-db.sql.gz
gunzip -f /srv/datadump/urbanfootprint-sacog-web-db.sql.gz

# import sample web database
psql -U postgres -c "DROP DATABASE IF EXISTS urbanfootprint;"
psql -U postgres -c "CREATE DATABASE urbanfootprint;"
psql -U postgres -c "GRANT ALL ON DATABASE urbanfootprint TO calthorpe;"
psql -U postgres urbanfootprint < /srv/datadump/urbanfootprint-sacog-web-db.sql

# finish installation and deployment process
su - calthorpe -c "/srv/calthorpe_env/bin/fab -f /srv/calthorpe/urbanfootprint/footprint/installer localhost quickstart"

external_ip=$(curl -s 'https://api.ipify.org')
echo ""
echo "********************************************************************"
echo "********************************************************************"
echo ""
echo "  UrbanFootprint quickstart is complete. Open your web browser to:"
echo "    http://${external_ip}/"
echo "  using the following default credentials:"
echo "    user: admin@urbanfootprint.net"
echo "    pass: admin@uf"
echo ""
echo "********************************************************************"
echo "********************************************************************"
echo ""

exit 0
