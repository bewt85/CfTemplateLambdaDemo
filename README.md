# CfTemplateLambdaDemo

This project is part demo, part aide memoire.  It is mean to demonstrate a couple of different ways you can use AWS Lambda 
and AWS CloudFormation; it is intentionally a bit more involved than other examples.

Lambda is used both as a Custom Resource within a CloudFormation template (to create SSL certificates) and as an event 
reactor to spin up infrastructure.  The result looks a little like a simple Platform as a Service.

Although similar in principle to how we build our infrastructure at [drie](https://drie.co); I have taken a number of 
horrible shortcuts to simplify things.  For example things go horribly wrong if two apps have the same name and this 
doesn't encrypt the backend SSL certificates.
