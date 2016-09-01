# We need an init system for current UF configuration
# so we're using phusion's Ubuntu 140.04 baseimage
FROM calthorpeanalytics/phusion-baseimage:trusty

# Set the locale
# RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN apt-get update && apt-get install -y \
        build-essential \
        curl \
        gcc \
        git \
        libffi-dev \
        libssl-dev \
        python \
        python-dev \
        python-pip \
        python-yaml \
        sudo

RUN pip install ansible==1.9.6

# Add playbooks to the Docker image
ADD provisioning /opt/uf-provisioning
WORKDIR /opt/uf-provisioning

# TODO:
#   I currently don't understand this... taken from the bottom of:
#   http://ansible.pickle.io/post/86598332429/running-ansible-playbook-in-localhost
RUN mkdir -p /etc/ansible
RUN echo "localhost ansible_connection=local" > /etc/ansible/hosts

# Run Ansible to configure the Docker image
RUN ansible-galaxy install -r galaxy-roles.yml

# Don't install postgresql in the image
# RUN ansible-playbook -v provisioning/servers-web.yml

# Install postgresql in the image
RUN ansible-playbook -v site.yml

# Use baseimage-docker's init system.
# CMD ["/sbin/my_init"]
