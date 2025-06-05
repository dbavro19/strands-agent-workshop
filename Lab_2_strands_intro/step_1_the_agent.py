from strands import Agent
from strands.models import BedrockModel



bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",  # Specify the model ID
    temperature=0.7,  # Control randomness (0.0 to 1.0)
    top_p=0.9,  # Control diversity
    max_tokens=2000,  # Maximum response length
    region_name="us-east-1"  # AWS region where you have model access
)

#us.anthropic.claude-3-5-haiku-20241022-v1:0"

agent = Agent(model=bedrock_model)
result = agent("What is the most popular sport in the world?")



print("-----------------------Now WITH A SYSTEM PROMPT--------------------------------")


#SECOND AGENT

agent2 = Agent(
  model = bedrock_model,
  system_prompt="""
You convert csv structures to json. 
You may only respond in valid json.
Mask any Personally Indentifiable Infomration (PII) with the first character followed by the * replacing each subsequent character for that word (example: Dom Bavaro -> D** B*****) 
"""
)

agent2("""
#Date,Ticker,Price,Volume,MarketCap,PE_Ratio,Revenue,Analyst
#2024-01-15,AAPL,185.64,52847291,2847000000000,28.5,394328000000,Sarah Mitchell
#2024-01-15,MSFT,402.56,23156789,2991000000000,34.2,245122000000,David Chen
#2024-01-15,GOOGL,142.87,28934567,1784000000000,25.8,307394000000,Maria Rodriguez
#2024-01-15,AMZN,153.75,41267834,1598000000000,52.1,574785000000,James Thompson
#2024-01-15,TSLA,219.16,89456723,697000000000,71.3,96773000000,Emily Johnson
#""")