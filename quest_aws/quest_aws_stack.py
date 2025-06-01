from aws_cdk import (
    Stack,
    pipelines,
    SecretValue
)
from constructs import Construct
from quest_aws.stages.prod_stage import ProdStage 
from quest_aws.stages.dev_stage import DevStage

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

        # Add unit test step (fail pipeline on test failure)
        test_step = pipelines.ShellStep("RunUnitTests",
            input=git_input,
            install_commands=[
                "pip install -r requirements.txt"
            ],
            commands=[
                "pytest tests/unit"
            ]
        )
        dev_stage = DevStage(self, "DevStage")
        pipeline.add_stage(dev_stage,
            pre=[test_step]
        )

        prod_stage = ProdStage(self, "ProdStage")
        pipeline.add_stage(prod_stage,
            pre=[pipelines.ManualApprovalStep("ApproveProdDeploy")]
        )
