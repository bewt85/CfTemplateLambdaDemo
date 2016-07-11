# App Instance Setup

This is the app that runs on our hacky PaaS.  It is a [simple app](hello.py) written in python using the Flask
(micro) framework which tells you about some of the configuration.

The code is loaded onto the instance through a git clone initiated by the UserData.  [A setup script](setup.sh) then
installs the dependencies, sets up a [systemd unit](app.service) to run [the service](app.sh) using Twisted and starts
it running.  There is also an [optional script](setup_backend_SSL.py) which downloads an SSL certificate from S3 and
uses it to run a stunnel service.