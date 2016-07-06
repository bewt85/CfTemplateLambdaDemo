#!/bin/bash

set -eu -o pipefail

cd /home/ubuntu/web
python3 -m http.server 8080
