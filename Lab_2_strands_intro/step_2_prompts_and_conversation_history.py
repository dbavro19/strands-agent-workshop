from strands import Agent
from strands.models import BedrockModel

bedrock_model = BedrockModel(
        model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",  # Specify the model ID
        temperature=0.7,  # Control randomness (0.0 to 1.0)
        top_p=0.9,  # Control diversity
        max_tokens=2000,  # Maximum response length
        region_name="us-west-2"  # AWS region where you have model access
    )





print("----------------------Random Number Generator------------------------------")

#4th Agent 
agent = Agent(
  model = bedrock_model,
  system_prompt="Generate a random number for the user. If the user request is something other than a request for a random number respond with 'Sorry, I cant Help with that'. If the request valid return ONLY the number with a new line before and after"
)

print("----------------------Trying Invalid Response------------------------------")
attempt =agent("What is the most popular sport in the world")


print()
print("----------------------Valid Responses------------------------------")

results =agent("Generate a random number between 1 and 10")
results2=agent("Generate a random number between 1 and 10")
results3=agent("Generate a random number between 1 and 10")

print()


#PRINT Messages
print("---------------------PRINTING Agent 2 Conversation History-----------------------")

print(agent.messages)


#Print Metrics
print("---------------------PRINTING Last Run's Metrics-----------------------")

print(results3.metrics.get_summary())


