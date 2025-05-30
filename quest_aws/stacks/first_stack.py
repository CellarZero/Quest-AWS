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

        queue_name = "dev-DataPipelineQueue" if environment == "dev" else "prod-DataPipelineQueue"

        print(f"Running {environment} environment")
        sync_lambda = _lambda.Function(self, f"SyncBLSandAPIData-{environment}",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="test.lambda_handler",
            code=_lambda.Code.from_asset("quest_aws/lambda_functions"),
            timeout=Duration.minutes(5),
        )
        
        # 1. S3 Bucket
        # bucket = s3.Bucket.from_bucket_name(self, "RearcQuestV2Bucket", "rearcquestv2")

        # # 2. SQS Queue
        # # queue = sqs.Queue(self, "DataPipelineQueue",
        # #     visibility_timeout=Duration.seconds(60))
        # queue = sqs.Queue.from_queue_name(self, "RearcNotificationQueue", queue_name)

        # # Lambda Function 1: SyncBLSandAPI
        # sync_lambda = _lambda.Function(self, f"SyncBLSandAPIData-{environment}",
        #     runtime=_lambda.Runtime.PYTHON_3_9,
        #     handler="sync_bls_api.lambda_handler",
        #     code=_lambda.Code.from_asset("lambda"),
        #     timeout=Duration.minutes(5),
        #     environment={
        #         "BUCKET_NAME": bucket.bucket_name
        #     }
        # )
        # bucket.grant_write(sync_lambda)

        # # Scheduled Rule to trigger sync_lambda daily
        # rule = events.Rule(self, f"DailyDataSyncRule-{environment}",
        #     schedule=events.Schedule.rate(Duration.days(1))
        # )
        # rule.add_target(targets.LambdaFunction(sync_lambda))

        # # Lambda Function 2: AnalyticsProcessor
        # analytics_lambda = _lambda.Function(self, f"Analytics-{environment}",
        #     runtime=_lambda.Runtime.PYTHON_3_9,
        #     handler="analysis.lambda_handler",
        #     code=_lambda.Code.from_asset("lambda"),
        #     timeout=Duration.minutes(5),
        #     environment={
        #         "BUCKET_NAME": bucket.bucket_name
        #     }
        # )
        # bucket.grant_read(analytics_lambda)
        # queue.grant_consume_messages(analytics_lambda)

        # # Ensure SQS visibility timeout is at least Lambda timeout
        # # You MUST ensure this is true in actual queue settings

        # # Event source mapping: SQS triggers analytics Lambda
        # analytics_lambda.add_event_source_mapping(f"SQSLambdaTrigger-{environment}",
        #     event_source_arn=queue.queue_arn,
        #     batch_size=1
        # )

        # # Add S3 event notification for population JSON file
        # bucket.add_event_notification(
        #     s3.EventType.OBJECT_CREATED_PUT,
        #     s3n.SqsDestination(queue),
        #     s3.NotificationKeyFilter(prefix="population-data/", suffix=".json")
        # )
