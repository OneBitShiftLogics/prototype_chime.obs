import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as iam from 'aws-cdk-lib/aws-iam';

export class MeetChObsStack extends cdk.Stack {
    constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // Create DynamoDB Table
        const meetingsTable = new dynamodb.Table(this, 'MeetingsTable', {
            partitionKey: { name: 'MeetingId', type: dynamodb.AttributeType.STRING },
            billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
        });

        // IAM Role for Lambda
        const lambdaRole = new iam.Role(this, 'LambdaChimeRole', {
            assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
        });

        lambdaRole.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName("service-role/AWSLambdaBasicExecutionRole"));
        lambdaRole.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName("AmazonChimeFullAccess"));

        // **Fix: Ensure Lambda uses correct function names**
        const startMeetingLambda = new lambda.Function(this, 'StartMeetingLambda', {
            functionName: 'StartMeetingLambda',  // ✅ Explicit function name
            runtime: lambda.Runtime.PYTHON_3_9,
            handler: 'start_meeting.lambda_handler',  // ✅ Correct handler
            code: lambda.Code.fromAsset('lambda'),
            environment: {
                TABLE_NAME: meetingsTable.tableName,
            },
            role: lambdaRole,
        });

        const endMeetingLambda = new lambda.Function(this, 'EndMeetingLambda', {
            functionName: 'EndMeetingLambda',  // ✅ Explicit function name
            runtime: lambda.Runtime.PYTHON_3_9,
            handler: 'end_meeting.lambda_handler',  // ✅ Correct handler
            code: lambda.Code.fromAsset('lambda'),
            environment: {
                TABLE_NAME: meetingsTable.tableName,
            },
            role: lambdaRole,
        });

        // Grant permissions to Lambda
        meetingsTable.grantReadWriteData(startMeetingLambda);
        meetingsTable.grantReadWriteData(endMeetingLambda);

        // API Gateway
        const api = new apigateway.RestApi(this, 'ChimeApi');

        const joinResource = api.root.addResource('new').addResource('join').addResource('{bot_name}');
        joinResource.addMethod('POST', new apigateway.LambdaIntegration(startMeetingLambda));

        const endResource = api.root.addResource('meeting').addResource('{meeting_id}').addResource('end');
        endResource.addMethod('POST', new apigateway.LambdaIntegration(endMeetingLambda));

        new cdk.CfnOutput(this, 'ApiGatewayUrl', { value: api.url });
    }
}
