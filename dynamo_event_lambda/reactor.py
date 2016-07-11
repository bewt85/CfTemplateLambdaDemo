import boto3
import botocore
import json
import re
import logging

logger = logging.getLogger("CfReactor")
logger.setLevel(logging.DEBUG)

dynamodb = boto3.resource('dynamodb')
cloudformation = boto3.resource('cloudformation')


with open("config.json", "r") as config_file:
    config = json.load(config_file)

with open("cf_template.json", "r") as template_file:
    cf_template_content = template_file.read()

app_db = dynamodb.Table(config["app_database"])

def app_stack_name(app_name):
    return "demo-app-{}".format(app_name)


def app_name_from_stack(stack_name):
    try:
        (app_name,) = re.match("^demo-app-(.+)$", stack_name).groups()
    except (ValueError, IndexError, AttributeError):
        raise ValueError("Could not parse app_name from '{}'".format(stack_name))
    else:
        return app_name


def parse_cf_message(message):
    return {unicode(k): unicode(v.strip("'"))
            for k, v in re.findall("(\S+)=(\'.*?\')", message, re.DOTALL)}


def get_app_data(app_name):
    response = app_db.get_item(Key={'Name': app_name})
    return response.get("Item")


def get_app_stack(app_name):
    try:
        stack = cloudformation.Stack(name=app_stack_name(app_name))
        stack.stack_status
        return stack
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ValidationError':
            return None
        raise

def stack_outputs_to_dict(stack):
    try:
        return {o["OutputKey"]: o["OutputValue"] for o in stack.outputs}
    except TypeError:
        logging.debug("Failed to get outputs from stack")
        return {} # outputs = None


def stack_parameters_to_dict(stack):
    try:
        return {o["ParameterKey"]: o["ParameterValue"] for o in stack.parameters}
    except TypeError:
        logging.debug("Failed to get parameters from stack")
        return {} # parameters = None


class AppCfHandler(object):
    def handle(self, event, context):
        messages = map(lambda r: parse_cf_message(r['Sns']['Message']), event['Records'])
        for message in messages:
            self.handle_message(message)

    def handle_message(self, message):
        stack_name = message["StackName"]
        resource = message["LogicalResourceId"]
        resource_status = message['ResourceStatus']

        if resource != stack_name:
            logger.debug("We're only interested in changes to the stack {}, not {}".format(stack_name, resource))
            return

        app_name = app_name_from_stack(stack_name)
        stack = get_app_stack(app_name)
        handler = {
            "CREATE_COMPLETE": self.updated,
            "CREATE_IN_PROGRESS": self.set_deploying,
            "CREATE_FAILED": self.create_failed,
            "DELETE_COMPLETE": None,
            "DELETE_FAILED": None,
            "DELETE_IN_PROGRESS": None,
            "ROLLBACK_COMPLETE": self.update_failed,
            "ROLLBACK_FAILED": self.errors,
            "ROLLBACK_IN_PROGRESS": None,
            "UPDATE_COMPLETE": self.updated,
            "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS": None,
            "UPDATE_IN_PROGRESS": self.set_deploying,
            "UPDATE_ROLLBACK_COMPLETE": self.update_failed,
            "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS": None,
            "UPDATE_ROLLBACK_FAILED": self.errors,
            "UPDATE_ROLLBACK_IN_PROGRESS": None
        }.get(resource_status)
        if handler is None:
            logger.debug("CloudFormation event {} for {} is not handled".format(resource_status, stack_name))
        else:
            logger.debug("Handling CloudFormation event {} for {}".format(resource_status, stack_name))
            handler(app_name, stack, resource_status)


    def set_deploying(self, app_name, stack, resource_status):
        self._update_db(app_name, {}, (None, "deploying", "deploy_failed", "deployed", "update"), "deploying")


    def updated(self, app_name, stack, resource_status):
        stack_outputs = stack_outputs_to_dict(stack)
        update = {
            "LoadBalancer": stack_outputs.get("LoadBalancer", "Unknown")
        }
        self._update_db(app_name, update, (None, "deploying"), "deployed")
        check_stack_is_up_to_date(app_name)


    def create_failed(self, app_name, stack, resource_status):
        self._update_db(app_name, {}, ("deploying",), "deploy_failed")
        check_stack_is_up_to_date(app_name)


    def update_failed(self, app_name, stack, resource_status):
        stack_outputs = stack_outputs_to_dict(stack)
        update = {
            "LoadBalancer": stack_outputs.get("LoadBalancer", "Unknown")
        }
        self._update_db(app_name, update, (None, "deploying"), "deployed")
        check_stack_is_up_to_date(app_name)


    def errors(self, app_name, stack, resource_status):
        self._update_db(app_name, {}, ("deploying",), "deploy_failed")
        check_stack_is_up_to_date(app_name)


    def _update_db(self, app_name, updates, original_statuses, new_status):
        if new_status is not None:
            updates['status'] = new_status
        update_expression = "SET " + ", ".join(["#{0} = :{0}".format(k) for k in updates.keys()])
        attribute_names = {"#{}".format(k): str(k) for k in updates.keys()}
        attribute_values = {":{}".format(k): v for k,v in updates.items()}
        try:
            if original_statuses is not None:
                condition_expressions = []
                if None in original_statuses:
                    original_statuses = [status for status in original_statuses if status is not None]
                    condition_expressions.append("attribute_not_exists(#status)")
                    attribute_names['#status'] = "status"
                if len(original_statuses) >= 1:
                    attribute_names['#status'] = "status"
                    original_status_map = {":new_status_{}".format(i+1): v for i,v in enumerate(original_statuses)}
                    condition_expressions.append("#status IN ({})".format(", ".join(original_status_map.keys())))
                    attribute_values.update(original_status_map)
                assert len(condition_expressions) >= 1, "Expected some original_statuses or None"
                app_db.update_item(
                    Key={'Name': app_name},
                    UpdateExpression=update_expression,
                    ExpressionAttributeNames=attribute_names,
                    ExpressionAttributeValues=attribute_values,
                    ConditionExpression=" OR ".join(condition_expressions)
                )
            else:
                app_db.update_item(
                    Key={'Name': app_name},
                    UpdateExpression=update_expression,
                    ExpressionAttributeNames=attribute_names,
                    ExpressionAttributeValues=attribute_values,
                 )
        except botocore.exceptions.ClientError as e:
            if "ConditionalCheckFailedException" in e.message:
                database_status = get_app_data(app_name).get("status")
                logger.debug("Failure updating details for {}; status {} wasn't in {}".format(app_name, database_status, repr(original_statuses)))
                return True
            else:
                raise
        else:
            return False


class DynamoHandler(object):
    def handle(self, event, context):
        apps_updated = {record['dynamodb']['Keys']['Name']['S'] for record in event['Records']}
        for app_name in apps_updated:
            logger.debug("Handling DynamoDB event for {}".format(app_name))
            check_stack_is_up_to_date(app_name)


def create_app_stack(app_name, scale, version):
    logger.info("Creating a app called {}".format(app_name))
    parameters = {
        "AppName": app_name,
        "AppsDomain": config['AppsDomain'],
        "AppsDomainSSLCertificate": config['AppsDomainSSLCertificate'],
        "KeyName": config['KeyName'],
        "Scale": str(scale),
        "Version": version,
        "CertificateBucket": config['CertificateBucket'],
        "CreateElbBackendCertificatesArn": config['CreateElbBackendCertificatesArn'],
        "Route53HostedZoneId": config['Route53HostedZoneId']
    }
    cloudformation.create_stack(
        StackName=app_stack_name(app_name),
        TemplateBody=cf_template_content,
        Parameters=[
            {'ParameterKey': key, 'ParameterValue': value} for key, value in parameters.items()
        ],
        Capabilities=[
            'CAPABILITY_IAM',
        ],
        NotificationARNs=[config['CloudFormationNotificationArn']]
    )

def check_stack_is_up_to_date(app_name):
        logger.info("Checking that app {} is up to date".format(app_name))

        stack = get_app_stack(app_name)
        dynamo_data = get_app_data(app_name)

        if dynamo_data is None:
            logger.debug("Deleting {}".format(app_name))
            if stack is not None:
                stack.delete()
            return
        if not stack:
            logger.debug("Checking that {} is created".format(app_name))
            create_app_stack(app_name, int(dynamo_data['Scale']), dynamo_data['Version'])
            return
        if not stack.stack_status.endswith("_COMPLETE"):
            logger.debug("Stack status '{}' of {} is not handled".format(stack.stack_status, app_name))
            return

        dynamo_parameters = {
            "Scale": str(int(dynamo_data["Scale"])),
            "Version": dynamo_data["Version"],
            "AppName": dynamo_data["Name"]
        }
        stack_parameters = stack_parameters_to_dict(stack)
        if {k: stack_parameters.get(k) for k in dynamo_parameters.keys()} != dynamo_parameters:
            logger.debug("{} has been updated, updating stack".format(app_name))
            stack_parameters.update(dynamo_parameters)
            stack.update(
                TemplateBody=cf_template_content,
                Parameters=[{"ParameterKey": k, "ParameterValue": v} for k, v in stack_parameters.items()],
                Capabilities=[
                    'CAPABILITY_IAM',
                ],
            )
        else:
            logger.info("{} is up to date, no changes to stack".format(app_name))


def lambda_handler(event, context):
    try:
        logger.debug(event)
        first_record = event['Records'][0]
        if 'Sns' in first_record:
            return AppCfHandler().handle(event, context)
        else:
            return DynamoHandler().handle(event, context)
    except Exception as e:
        logger.exception(e)
        raise
