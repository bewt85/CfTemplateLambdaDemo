#!/bin/bash

set -eu -o pipefail

apt-get update
apt-get install -y \
  git \
  stunnel4 \
  python \
  python-pip

# From Dave Dopson (http://stackoverflow.com/a/246128)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVICE_SCRIPT="${DIR}/app.service"

cp $SERVICE_SCRIPT /etc/systemd/system
chmod 0644 /etc/systemd/system/app.service

chmod 0744 "${DIR}/app.sh"

pip install --upgrade pip
pip install virtualenv
cd $DIR

if [ ! -f venv/bin/activate ]; then
  sudo -iHu ubuntu virtualenv ${DIR}/venv -p $(which python2)
fi

sudo -iHu ubuntu ${DIR}/venv/bin/pip install -r ${DIR}/requirements.txt