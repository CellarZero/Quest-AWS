import aws_cdk as core
import aws_cdk.assertions as assertions

from quest_aws.quest_aws_stack import QuestAwsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in quest_aws/quest_aws_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = QuestAwsStack(app, "quest-aws")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
