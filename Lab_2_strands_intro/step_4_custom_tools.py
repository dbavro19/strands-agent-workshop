from strands import Agent
from strands_tools import calculator, use_aws
from strands.models import BedrockModel
from custom_tools import get_weather #IMPORTING MY CUSTOM TOOL


bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",  # Specify the model ID
    temperature=0.7,  # Control randomness (0.0 to 1.0)
    top_p=0.9,  # Control diversity
    max_tokens=2000,  # Maximum response length
    region_name="us-east-1"  # AWS region where you have model access
)

#us.anthropic.claude-3-5-haiku-20241022-v1:0"

agent = Agent(model=bedrock_model, tools=[calculator, get_weather, use_aws])
result = agent("What is 10 * 22 divided by tom brady's jersey number? Is that more or less than the current temperature in alaska")


# Access metrics through the AgentResult
print("")
print("---------------------Metrics-----------------")
print(f"Total tokens: {result.metrics.accumulated_usage['totalTokens']}")
print(f"Execution time: {sum(result.metrics.cycle_durations):.2f} seconds")
print(f"Tools used: {list(result.metrics.tool_metrics.keys())}")

#print(f"Cycle Count: {result.metrics.cycle_count}")
#print(f"Traces: {list(result.metrics.traces)}")


#print("SUMMARY")
#print(result.metrics.get_summary())
