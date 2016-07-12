# CfTemplateLambdaDemo

This project includes some simple and more advanced CloudFormation examples.  It also shows how Lambda can be used to power a Custom Resource within a more advanced example 
and how it can also be used to create a rudimentary Platform as a Service by listening for events.

## CloudFormation Templates

There are three [demo CloudFormation templates](cloudformation_template_examples):

* [Simple Example](cloudformation_template_examples/simple_app_template.json): Flask app in an autoscale group behind an ELB
* [VPC Example](cloudformation_template_examples/vpc_example_template.json): The Simple Example but in a custom VPC
* [HTTPS Example](cloudformation_template_examples/https_app_template.json): The VPC Example but behind Route53 and using SSL certificates on the ELB and to secure the backend connection

The third example shows how Lambda can power a Custom Resource to create SSL certificates.

## A Simple Platform as a Service

This repo also includes [another Lambda function](dynamo_event_lambda) which can be used with [HTTPS Example](cloudformation_template_examples/https_app_template.json) to make something which 
looks a little like a Platform as a Service (PaaS).  This Lambda subscibes to DynamoDB and CloudFormation events to create, update and delete CloudFormation stacks and to update the 
DynamoDB Table with the results of those changes.

Although similar in principle to how we build our infrastructure at [drie](https://drie.co); I have taken a number of 
horrible shortcuts to simplify things.  For example things go horribly wrong if two apps have the same name and this 
doesn't encrypt the backend SSL certificates.

## Dependencies

This demo was created using Ubuntu 15.04 with Python 2.7.  It might work with other stacks but it hasn't been tested.
Some of the demos need some existing AWS resources (e.g. a DynamoDB Table).  If there is sufficient interest, I'll put 
together a CloudFormation template to set these up; in the mean time there are instructions on what you need in the 
various READMEs.  The demo will only work in `us-east-1` or `eu-west-1`; other regions can be supported by updating 
the `Mapping` sections of the CloudFormation templates with details of alternative AMIs.
