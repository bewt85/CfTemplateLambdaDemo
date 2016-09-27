# AppDemoReactorLambda

This Lambda function powers our hacky PaaS.  It receives events from DynamoDB to create, update and delete app
instances.  It also monitors changes reported by stacks to update the status field in DynamoDB.

## Pre-requisites

This demo will only work in `eu-west-1` or `us-east-1`.

* A DynamoDB table called `apps-demo`
  * Primary partition key: Name
  * Uncheck "Use default settings"
  * Read capacity: 1;
  * Write Capacity: 1;
  * No sort key
* An SNS Topic called `AppDemoCloudFormationSns`
* A (sub-)domain managed by Route53
* A wildcard certificate managed by Amazon Certificate Manager for that domain
* An SSH key uploaded to IAM (to log into instances)
* Deploy the [CreateElbBackendCertificates](../certificate_lambda)

## Setup

* Creating an IAM policy and IAM role with permissions at least as generous as the [lambda_policy](lambda_policy.json)
* Update your config.json with the details of your pre-requisites
* Run [package.sh](package.sh) on a Linux machine (it might work on OSX but it isn't tested)
* Create a new Python 2.7 Lambda function called `AppDemoReactorLambda`
  * Set the runtime to `Python 2.7`
  * Upload the ZIP file which is created to your new Lambda
  * Set the handler to `reactor.lambda_handler`
  * Use the new role you created
  * Set the Timeout to 30 seconds
  * Leave the default VPC settings
* In the triggers for the new lambda
  * Hook up to listen to events from the SNS Topic called `AppDemoCloudFormationSns`
  * Hook up to listen to events from the DynamoDB table called `apps-db` (keep the other default settings)

## Usage

Create a new Item in your DynamoDB Table.  It should have the following data:

* Name: a String
* Version: a String; Git commit or branch for this repo
* Scale: a Number; the number of instances to run (between 0 and 3)

Have a look in the CloudFormation console to see details of the created stack.  One of the outputs should include 
the URL for your app; it should also be updated in DynamoDB.

To update the app, make a change to DynamoDB.  NB that changes to master will not be redeployed.  Even if you 
trigger a stack update, the running app will not be updated unless a Parameter is changed which is used in the 
Launch Config.  You could do this by giving a commit SHA1 instead of the branch name.

To delete the stack, just delete the DynamoDB Item.

## Dependencies

* [Probably] Linux (tested on Ubuntu 15.04)
* Python 2.7
* virtualenv (`pip install virtualenv`)
