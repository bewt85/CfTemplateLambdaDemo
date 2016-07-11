#!/bin/bash

set -eu -o pipefail

export ZIP_FILE=$(pwd)/AppDemoReactorLambda_$(date +%Y%m%d%H%M).zip
zip $ZIP_FILE reactor.py
zip $ZIP_FILE config.json
zip $ZIP_FILE cf_template.json
echo "Created $ZIP_FILE for upload"
