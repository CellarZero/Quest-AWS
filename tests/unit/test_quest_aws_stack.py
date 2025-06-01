import pytest
import aws_cdk as cdk
from aws_cdk.assertions import Template, Match
from quest_aws.stacks.first_stack import QuestFirstStack

@pytest.mark.parametrize("environment,expected_bucket_name", [
    ("dev", "dev-quest-aws-bkt"),
    ("prod", "prod-quest-aws-bkt"),
])
def test_stack_resources(environment, expected_bucket_name):
    app = cdk.App()
    stack = QuestFirstStack(app, f"TestStack-{environment}", environment=environment)
    template = Template.from_stack(stack)

    # Check SQS Queue exists
    template.has_resource_properties("AWS::SQS::Queue", {
        "VisibilityTimeout": 60
    })

    # Check Lambda function SyncBLSandAPIData
    template.has_resource_properties("AWS::Lambda::Function", Match.object_like({
        "Handler": "sync_bls_api.lambda_handler",
        "Environment": {
            "Variables": {
                "BUCKET_NAME": expected_bucket_name
            }
        }
    }))

    # Check Lambda function Analytics
    template.has_resource_properties("AWS::Lambda::Function", Match.object_like({
        "Handler": "analysis.lambda_handler",
        "Environment": {
            "Variables": {
                "BUCKET_NAME": expected_bucket_name
            }
        }
    }))

    # Check EventBridge Rule exists
    template.has_resource_properties("AWS::Events::Rule", {
        "ScheduleExpression": "rate(10 minutes)"
    })

    # Check Lambda Event Source Mapping exists
    template.resource_count_is("AWS::Lambda::EventSourceMapping", 1)