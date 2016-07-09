#!/usr/bin/env python

import boto3
import json
import os
import re
import shutil
import subprocess
import sys

from pwd import getpwnam

assert len(sys.argv) == 3, "Syntax is '{} S3_BUCKET S3_KEY'".format(sys.argv[0])
certificates_s3_bucket = sys.argv[1]
certificates_s3_key = sys.argv[2]

s3_client = boto3.client("s3")
response = s3_client.get_object(
    Bucket=certificates_s3_bucket,
    Key=certificates_s3_key,
)
content = response['Body'].read()
data = json.loads(content)

private_key = data['private_key'].encode("utf-8")
certificate = data['certificate'].encode("utf-8")

stunnel_pw = getpwnam('stunnel4')
stunnel_uid = stunnel_pw.pw_uid
stunnel_gid = stunnel_pw.pw_gid

stunnel_config = """\
output=/var/log/stunnel-elb-backend.log
pid=/var/run/stunnel4/elb-backend.pid

setuid=stunnel4
setgid=stunnel4

client=no

[ELB]
cert=/etc/stunnel/elb-backend-cert.pem
key=/etc/stunnel/elb-backend-private.key
accept=0.0.0.0:8443
connect=127.0.0.1:8080
"""

with open("/var/log/stunnel-elb-backend.log", "a") as log_file:
    os.chown("/var/log/stunnel-elb-backend.log", stunnel_uid, stunnel_gid)

with open("/etc/stunnel/elb-backend-cert.pem", 'w') as cert_file:
    os.chown("/etc/stunnel/elb-backend-cert.pem", stunnel_uid, stunnel_gid)
    cert_file.write(certificate.decode("utf-8"))
with open("/etc/stunnel/elb-backend-private.key", 'w') as key_file:
    os.chown("/etc/stunnel/elb-backend-private.key", stunnel_uid, stunnel_gid)
    os.chmod("/etc/stunnel/elb-backend-private.key", 0o0600)
    key_file.write(private_key.decode("utf-8"))
with open("/etc/stunnel/elb-backend.conf", 'w') as stunnel_conf_file:
    stunnel_conf_file.write(stunnel_config)

with open("/etc/default/stunnel4", 'r') as stunnel_launch_file:
    with open("/etc/default/stunnel4.new", 'w') as new_stunnel_launch_file:
        os.chmod("/etc/default/stunnel4.new", 0o0644)
        for line in stunnel_launch_file:
            if re.match("^\s*ENABLED\s*=\s*0\s*$", line):
                new_stunnel_launch_file.write("ENABLED=1\n")
            else:
                new_stunnel_launch_file.write(line)

shutil.move("/etc/default/stunnel4.new", "/etc/default/stunnel4")
subprocess.check_output(["systemctl", "restart", "stunnel4"])