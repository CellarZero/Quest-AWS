from aws_cdk import (
    Stack,
    Duration,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_sqs as sqs,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    aws_s3_notifications as s3n,
)
from constructs import Construct

class QuestFirstStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, environment: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket_name = "dev-quest-aws-bkt" if environment == "dev" else "prod-quest-aws-bkt"
        
        # 1. S3 Bucket
        bucket = s3.Bucket.from_bucket_name(self, "RearcQuestV2Bucket", bucket_name=bucket_name)

        # 2. SQS Queue
        queue = sqs.Queue(self, "DataPipelineQueue",
            visibility_timeout=Duration.seconds(60))

        dependencies_layer = _lambda.LayerVersion(
            self, f"DependenciesLayer",
            code=_lambda.Code.from_asset("quest_aws/lambda_layers/dependencies"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="Layer for boto3, pandas, beautifulsoup4, and requests"
        )
        numpy_layer = _lambda.LayerVersion.from_layer_version_arn(
            self, "NumpyLayer",
            "arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python39:28"
        )


        # Lambda Function 1: SyncBLSandAPI
        sync_lambda = _lambda.Function(self, f"SyncBLSandAPIData",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="sync_bls_api.lambda_handler",
            code=_lambda.Code.from_asset("quest_aws/lambda_functions"),
            timeout=Duration.seconds(60),
            environment={
                "BUCKET_NAME": bucket.bucket_name
            },
            layers=[dependencies_layer]
        )
        bucket.grant_write(sync_lambda)
        bucket.grant_read(sync_lambda)

        # Scheduled Rule to trigger sync_lambda daily
        rule = events.Rule(self, f"DailyDataSyncRule",
            schedule=events.Schedule.rate(Duration.days(1))
        )
        rule.add_target(targets.LambdaFunction(sync_lambda))

        # Lambda Function 2: AnalyticsProcessor
        analytics_lambda = _lambda.Function(self, f"Analytics",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="analysis.lambda_handler",
            code=_lambda.Code.from_asset("quest_aws/lambda_functions"),
            timeout=Duration.seconds(60),
            environment={
                "BUCKET_NAME": bucket.bucket_name
            },
            layers=[dependencies_layer, numpy_layer]
        )
        bucket.grant_read(analytics_lambda)
        queue.grant_consume_messages(analytics_lambda)

        # Event source mapping: SQS triggers analytics Lambda
        analytics_lambda.add_event_source_mapping(f"SQSLambdaTrigger-{environment}",
            event_source_arn=queue.queue_arn,
            batch_size=1
        )

        # Add S3 event notification for population JSON file
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED_PUT,
            s3n.SqsDestination(queue),
            s3.NotificationKeyFilter(prefix="population-data/", suffix=".json")
        )
