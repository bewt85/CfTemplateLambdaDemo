#!/bin/bash

set -eu -o pipefail

apt-get update
apt-get install -y \
  git \
  stunnel4

# From Dave Dopson (http://stackoverflow.com/a/246128)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVICE_SCRIPT="${DIR}/app.service"

cp $SERVICE_SCRIPT /etc/systemd/system

mkdir -p /home/ubuntu/web
touch /etc/app.conf
source /etc/app.conf
echo "<h1>Hello from ${APP_NAME:-"an unknown app"}</h1>
<p>There are (meant to be) ${APP_SCALE:-"an unknown number"} copies running</p>
<p>I am running version ${APP_VERSION:-"who knows"} of the app</p>" >> /home/ubuntu/web/index.html
chmod -R 644 /home/ubuntu/web/
