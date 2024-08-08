import json
import boto3
from datetime import datetime
from decimal import Decimal

# Custom JSON Encoder
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)

def lambda_handler(event, context):
    # Initialize boto3 clients
    ssm_client = boto3.client('ssm')
    ec2_client = boto3.client('ec2')
    
    # Parameters
    document_name = 'Disk-cleanup'  # Using a standard SSM document
    tag_key = 'Environment'  # Replace with your tag key
    tag_value = 'Production'  # Replace with your tag value
    
    try:
        # Describe instances with the specified tag key-value pair
        response = ec2_client.describe_instances(
            Filters=[
                {
                    'Name': f'tag:{tag_key}',
                    'Values': [tag_value]
                }
            ]
        )
        
        # Extract instance IDs
        instance_ids = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_ids.append(instance['InstanceId'])
        
        if not instance_ids:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'No instances found with the specified tags'}, cls=CustomEncoder)
            }
        
        # Trigger the SSM Run Command
        ssm_response = ssm_client.send_command(
            InstanceIds=instance_ids,
            DocumentName=document_name
        )
        
        # Return the command ID and other response details
        return {
            'statusCode': 200,
            'body': json.dumps(ssm_response, cls=CustomEncoder)
        }
    
    except Exception as e:
        # Handle exceptions and return the error message
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}, cls=CustomEncoder)
        }
