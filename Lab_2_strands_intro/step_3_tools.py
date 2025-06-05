from strands import Agent
from strands.models import BedrockModel
from strands_tools import calculator, use_aws

bedrock_model = BedrockModel(
        model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",  # Specify the model ID
        temperature=0.7,  # Control randomness (0.0 to 1.0)
        top_p=0.9,  # Control diversity
        max_tokens=2000,  # Maximum response length
        region_name="us-west-2"  # AWS region where you have model access
    )


#Without a Tool

agent_no_tools = Agent(
  model = bedrock_model,
  system_prompt="""
You are a helpful assistant. Help answer the users requests. Use the tools that have been provided if relevant
"""
)

#Agent WITH tje use_aws tool

agent_with_tools = Agent(
  model = bedrock_model,
  tools=[use_aws],
  system_prompt="""
You are a helpful assistant. Help answer the users requests. Use the tools that have been provided if relevant
"""
)

print("----------------------Trying Agent with no Tools------------------------------")
print()

results = agent_no_tools("is there an s3 bucket in my account called strands-dbavaro-bucket-2, if not create one")

print()
print("----------------------Trying Agent WITH Tools------------------------------")
print()

results2 =agent_with_tools("is there an s3 bucket in my account called strands-dbavaro-bucket-2, if not create one")


print()
print("---------------------PRINTING Agent Full Metrics-----------------------")
print()
print(results.metrics.get_summary())







