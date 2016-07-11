# AppDemoReactorLambda

This Lambda function powers our hacky PaaS.  It receives events from DynamoDB to create, update and delete app
instances.  It also monitors changes reported by stacks to update the status field in DynamoDB.

## Pre-requisites

* A DynamoDB table called `apps-db`
  * Read capacity: 1;
  * Write Capacity: 1;
  * Primary partition key: Name
  * No sort key
* An SNS Topic called `AppDemoCloudFormationSns`
* A (sub-)domain managed by Route53
* A wildcard certificate managed by Amazon Certificate Manager for that domain
* An SSH key uploaded to IAM (to log into instances)
* Deploy the [CreateElbBackendCertificates](../certificate_lambda)

## Setup

* Creating an IAM policy and IAM role with permissions at least as generous as the [lambda_policy](lambda_policy.json)
* Update your config.json with the details of your pre-requisites
* Create a new Python 2.7 Lambda function called `AppDemoReactorLambda`
* Use the new role you created
* Run [package.sh](package.sh) on a Linux machine (it might work on OSX but it isn't tested)
* Upload the ZIP file which is created to your new Lambda
* Hook up to listen to events from the SNS Topic called `AppDemoCloudFormationSns`
* Hook up to listen to events from the DynamoDB table called `apps-db`

## Dependencies

* [Probably] Linux (tested on Ubuntu 15.04)
* Python 2.7
* virtualenv (`pip install virtualenv`)