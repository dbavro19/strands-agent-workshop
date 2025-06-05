import boto3
import json
import step_3_random_number_tool

def invoke_model(message):

    tools = step_3_random_number_tool.get_tool_definition()

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


    response = bedrock.converse(
        modelId="us.anthropic.claude-3-5-haiku-20241022-v1:0",
        inferenceConfig={
            "maxTokens": 2000,
            "temperature": 0
        },
        toolConfig={
            "tools": tools
        },
        system=[{"text": system_prompt}],
        messages=messages
    )

    # In your invoke_model function, update the tool handling:
    if get_stop_reason(response) == 'tool_use':
        tool_use = response['output']['message']['content'][1]['toolUse']
        if tool_use['name'] == 'random_number_generator':
            min_val = tool_use['input']['min']
            max_val = tool_use['input']['max']
            result = step_3_random_number_tool.random_number_generator(min_val, max_val)

        else:
            result = response['output']['message']['content'][0]['text']


    return result


def get_stop_reason(response):
    return response['stopReason']



for i in range(5):
    print(f"Attempt {i+1}:")
    result = invoke_model("Give me a random number between 1 and 10")
    print(result)
