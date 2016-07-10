#!/bin/bash

set -eu -o pipefail

export ZIP_FILE=$(pwd)/DrieAppBackendCertificates_$(date +%Y%m%d%H%M).zip
zip $ZIP_FILE lambda_function.py
zip $ZIP_FILE cfnresponse.py
echo "Created $ZIP_FILE for upload"
