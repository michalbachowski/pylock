#!/bin/sh

# install core packages
if [ -x $(which apt-get) ]; then
    # old Python versions
    sudo add-apt-repository ppa:deadsnakes/ppa
    # update packages
    apt-get update

    # Pythons
    apt-get install --assume-yes \
        python-pip \
        software-properties-common \
        python3.1 python3.1-minimal \
        python3.3 python3.3-minimal \
        python3.4 python3.4-minimal \
        python3.5 python3.5-minimal \
        python3.6 python3.6-minimal
fi

# install python packages
if [ -x $(which pip) ]; then
    pip install --upgrade pip
    pip install 'tox==2.7.0' -r/home/vagrant/app/test/requirements.txt
fi

if [ -x $(which cpan) ]; then
    # cpan first time config
    if [ ! -d ~/.cpan ]; then
        (echo) | cpan
    fi
    cpan Test::Exception
fi

exit 0

