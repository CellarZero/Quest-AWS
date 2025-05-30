from aws_cdk import (
    Stack,
    pipelines,
    SecretValue
)
from constructs import Construct
from quest_aws.stages.prod_stage import ProdStage 
from quest_aws.stages.test_stage import TestStage 

class QuestAwsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "QuestAwsQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
        git_input = pipelines.CodePipelineSource.git_hub(
            repo_string="CellarZero/Quest-AWS",
            branch="main",
            # connection_arn="arn:aws:codestar-connections:eu-central-1:372775801647:connection/5ba58d40-4796-443d-bd86-37c610f0e665"
            authentication=SecretValue.secrets_manager("github-token"),
        )


        pipeline = pipelines.CodePipeline(self, "Pipeline",
            pipeline_name="RearcQuestCICD",
            synth=pipelines.ShellStep("Synth",
                input=git_input,

                install_commands=[
                    "npm install -g aws-cdk",
                    "pip install -r requirements.txt"
                ],
                commands=[
                    # "pytest",
                    "cdk synth"
                ]
            )
        )

        # Add stages
        pipeline.add_stage(TestStage(self, "TestStage"))

        prod_stage = ProdStage(self, "ProdStage")
        pipeline.add_stage(prod_stage,
            pre=[pipelines.ManualApprovalStep("ApproveProdDeploy")]
        )
