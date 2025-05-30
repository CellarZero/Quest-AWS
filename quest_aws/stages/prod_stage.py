from aws_cdk import Stage
from constructs import Construct
from quest_aws.stacks.first_stack import QuestFirstStack

class ProdStage(Stage):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        QuestFirstStack(self, "RearcQuestProd", environment="prod")
