from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
#from custom_tools import get_weather #IMPORTING MY CUSTOM TOOL


bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",  # Specify the model ID
    temperature=0.7,  # Control randomness (0.0 to 1.0)
    top_p=0.9,  # Control diversity
    max_tokens=2000,  # Maximum response length
    region_name="us-east-1"  # AWS region where you have model access
)

#ADDING MCP CLIENTS
#SYTAX CAN DIFFER BETWEEN OS


# Create MCP client for DuckDuckGo server
ddg_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="uvx", 
        args=["duckduckgo-mcp-server"]
    )
))
    
# Use context manager to ensure proper connection lifecycle
with ddg_mcp_client:
    # Get available tools from the MCP server
    # DuckDuckGo MCP provides: search() and fetch_content() tools
    ddg_tools = ddg_mcp_client.list_tools_sync()
    #custom_tools = [get_weather]
    agent_tools = [*ddg_tools]
        
    #print(f"Available tools: {[tool.name for tool in tools]}")
        
    # Create Strands agent with MCP tools
    agent = Agent(tools=agent_tools)
    
    result=agent("Whats the latest aws news?")

# Access metrics through the AgentResult
print("")
print("---------------------Metrics-----------------")
print(f"Total tokens: {result.metrics.accumulated_usage['totalTokens']}")
print(f"Execution time: {sum(result.metrics.cycle_durations):.2f} seconds")
print(f"Tools used: {list(result.metrics.tool_metrics.keys())}")