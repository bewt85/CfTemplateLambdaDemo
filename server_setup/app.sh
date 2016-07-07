#!/bin/bash

set -eu -o pipefail

# From Dave Dopson (http://stackoverflow.com/a/246128)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $DIR
set +u
source venv/bin/activate
set -u

export $(cat /etc/app.conf | xargs)
twistd -n web --wsgi hello.app -p 8080
