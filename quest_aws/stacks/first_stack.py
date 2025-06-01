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
         
        # if environment == "dev":
        #     queue_name = "dev-DataPipelineQueue" 
        #     bucket_name = "dev-quest-aws-bkt"
        # else :
        #     queue_name = "prod-DataPipelineQueue"
        #     bucket_name = "prod-quest-aws-bkt"
        
        # bucket = s3.Bucket.from_bucket_name(self, "ExistingBucket", bucket_name)

        # queue = sqs.Queue.from_queue_attributes(
        #     self, "ExistingQueue",
        #     queue_arn=f"arn:aws:sqs:{self.region}:{self.account}:{queue_name}",
        #     queue_url=f"https://sqs.{self.region}.amazonaws.com/{self.account}/{queue_name}"
        # )   

        # # queue = sqs.Queue.from_queue_name(self, "ExistingQueue", queue_name)

        # sync_lambda = _lambda.Function(self, f"{environment}-SyncLambda",
        #     runtime=_lambda.Runtime.PYTHON_3_9,
        #     handler="lambda_functions.sync_bls_api.lambda_handler",
        #     code=_lambda.Code.from_asset("quest_aws/lambda_functions"),
        #     timeout=Duration.minutes(1),
        #     environment={"BUCKET_NAME": bucket.bucket_name}
        # )
        # bucket.grant_write(sync_lambda)

        # events.Rule(self, f"{environment}-DailySyncRule",
        #     schedule=events.Schedule.rate(Duration.days(1)),
        #     targets=[targets.LambdaFunction(sync_lambda)]
        # )

        # analytics_lambda = _lambda.Function(self, f"AnalyticsLambda-{environment}",
        #     runtime=_lambda.Runtime.PYTHON_3_9,
        #     handler="lambda_functions.analysis.lambda_handler",
        #     code=_lambda.Code.from_asset("quest_aws/lambda_functions"),
        #     timeout=Duration.minutes(1),
        #     environment={"BUCKET_NAME": bucket.bucket_name}
        # )
        # bucket.grant_read(analytics_lambda)
        # queue.grant_consume_messages(analytics_lambda)

        # analytics_lambda.add_event_source_mapping(
        #     f"-{environment}-SQSTrigger",
        #     event_source_arn=queue.queue_arn,
        #     batch_size=1
        # )

        # bucket.add_event_notification(
        #     s3.EventType.OBJECT_CREATED_PUT,
        #     s3n.SqsDestination(queue),
        #     s3.NotificationKeyFilter(prefix="population-data/", suffix=".json")
        # )


        
        #Sample lambda function for testing
        # print(f"Running {environment} environment")
        # sync_lambda = _lambda.Function(self, f"SyncBLSandAPIData-{environment}",
        #     runtime=_lambda.Runtime.PYTHON_3_9,
        #     handler="lambda_functions.test.lambda_handler",
        #     code=_lambda.Code.from_asset("quest_aws/lambda_functions"),
        #     timeout=Duration.minutes(5),
        # )
        
        # 1. S3 Bucket
        bucket = s3.Bucket.from_bucket_name(self, "RearcQuestV2Bucket", "dev-quest-aws-bkt")

        # 2. SQS Queue
        queue = sqs.Queue(self, "dev-DataPipelineQueue",
            visibility_timeout=Duration.seconds(60))
        # queue = sqs.Queue.from_queue_name(self, "RearcNotificationQueue", queue_name)

        dependencies_layer = _lambda.LayerVersion(
            self, f"DependenciesLayer-{environment}",
            code=_lambda.Code.from_asset("quest_aws/lambda_layers/dependencies"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="Layer for boto3, pandas, beautifulsoup4, and requests"
        )
        numpy_layer = _lambda.LayerVersion.from_layer_version_arn(
            self, "NumpyLayer",
            "arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python39:28"
        )


        # Lambda Function 1: SyncBLSandAPI
        sync_lambda = _lambda.Function(self, f"SyncBLSandAPIData-{environment}",
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
        rule = events.Rule(self, f"DailyDataSyncRule-{environment}",
            schedule=events.Schedule.rate(Duration.minutes(10))
        )
        rule.add_target(targets.LambdaFunction(sync_lambda))

        # Lambda Function 2: AnalyticsProcessor
        analytics_lambda = _lambda.Function(self, f"Analytics-{environment}",
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

        # Ensure SQS visibility timeout is at least Lambda timeout
        # You MUST ensure this is true in actual queue settings

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
