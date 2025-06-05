import boto3
import json

def invoke_model(message):

    # Configure the client 
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-west-2'
    )


    system_prompt="""
You are a helpful assistant
"""

    messages = [{
        'role': 'user',
        'content': [{'text': message}]
    }]

    # Make the API call

    body = {
        "modelId": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
        "inferenceConfig": {
            "maxTokens": 1024,
            "temperature": 0
        },
        "system": [{"text": system_prompt}],
        "messages": messages
    }

    response = bedrock.converse(**body)

    result = response['output']['message']['content'][0]['text']

    return result


for i in range(5):
    print(f"Attempt {i+1}:")
    result = invoke_model("Give me a random number between 1 and 10")
    print(result)
