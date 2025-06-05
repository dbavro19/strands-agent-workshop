import boto3
import botocore
from strands import tool
import streamlit as st
#from tool_management import get_tools

@tool
def create_plan(strategy_description: str, session_id: str):
    """
    Create a detailed backtesting plan for a trading strategy.
        
    Args:
        strategy_description: Description of the trading strategy to backtest
        session_id: unique id of the agent session
            
    Returns:
        Dictionary containing the plan in markdown and structured format
    """

    #tools = get_tools()
    tools="""
1. search_web

Description: Real-time web search for general topics
Input: Query string
Output: Search results and web content

2. get_daily_historical_stock_data

Description: Historical daily OHLCV stock data (100 days or 20+ years)
Input: Symbol (required), outputsize (compact/full)
Output: Daily price history with metadata

3. get_stock_quote

Description: Latest real-time price and volume data
Input: Symbol
Output: Current price, change, volume, trading metrics

4. get_earnings_transcript

Description: Earnings call transcripts with LLM sentiment analysis
Input: Symbol, quarter (YYYYQM format)
Output: Full transcript text with sentiment scoring

5. get_earnings_calendar

Description: Upcoming earnings announcements schedule
Input: Symbol (optional), horizon (3/6/12 months)
Output: List of upcoming earnings dates and companies

6. get_company_overview

Description: Comprehensive company fundamentals and financial ratios
Input: Symbol
Output: 59+ metrics including P/E, market cap, margins, growth rates
"""
    


    # Create a specialized planning agent with detailed instructions
    planning_prompt = f"""
Research and Backtesting Plan Generation Agent

You are an expert research and backtesting planning agent that creates comprehensive, executable plans for complex financial analytical tasks. You specialize in breaking down sophisticated research questions into clear, sequential steps that can be executed by specialized tools.

## Your Role

Create detailed research plans that:
- Address the specific research question or objective provided
- Break complex analysis into logical, sequential steps
- Specify exactly which tools to use for each step
- Define precise inputs and expected outputs
- Include validation criteria for each step
- Ensure each step builds toward answering the core question

## Available Tools

{tools}

## Plan Structure

Generate your plan in markdown format with the following sections:

### Research Overview
- Clear restatement of the research question/objective
- Key assumptions and scope boundaries
- Expected timeline and resource requirements
- Primary success metrics

### Execution Plan

For each step, specify:
1. **Step Name**: Clear, descriptive name
2. **Tool to Use**: Which specific tool will be used (must match available tools)
3. **Input Parameters**: Exact data sources, parameters, and configurations needed
4. **Expected Output**: Specific deliverables and insights this step will produce
5. **Success Criteria**: How to validate the step completed successfully
6. **Dependencies**: Which previous steps must complete first

### Example Step Format:
```
### Step X: [Descriptive Name]
- **Tool**: [Exact tool name]
- **Input**: [Specific parameters, data sources, configurations]
- **Output**: [Detailed description of deliverables]
- **Success Criteria**: [Measurable validation criteria]
- **Dependencies**: [Required preceding steps or "None"]
```

### Key Parameters
- Include any critical assumptions, thresholds, or configuration values
- Specify data requirements and quality standards
- Define risk management or error handling approaches

### Expected Deliverables
- List the final outputs that will answer the research question
- Specify format and presentation requirements
- Include key metrics or insights to be generated

## Quality Standards

Ensure your plan is:
- **Specific**: Each step has clear, actionable instructions
- **Sequential**: Steps build logically toward the research objective
- **Tool-Aware**: Only uses available tools with correct parameters
- **Measurable**: Success criteria are objective and verifiable
- **Complete**: Plan fully addresses the research question
- **Error-Resistant**: Includes validation and error handling

## Plan Focus

Your plan should be:
- Focused on answering the core research question
- Efficient in tool usage and resource allocation
- Comprehensive in addressing all aspects of the question
- Practical for execution by the available tools
- Structured to provide incremental insights throughout execution
    """

    config = botocore.config.Config(connect_timeout=500, read_timeout=500)
    bedrock = boto3.client('bedrock-runtime' , 'us-east-1', config = config)
        
    user_prompt=f"""
<user_input>
Create a detailed backtesting plan for: {strategy_description}
</user_input>
"""
    
    message = {
        "role": "user",
        "content": [
            {
                "text": user_prompt
            }
        ]
    }
        
    # Generate the plan
    messages = [message]
    #invoke the model
    response = bedrock.converse(
        modelId= "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        system=[{"text": planning_prompt}],
        messages=messages,
        inferenceConfig = {
            "maxTokens": 4096,
            "temperature": 0.1,
        }
    )

    plan_markdown=response['output']['message']['content'][0]['text']

    with st.expander("Generated Plan"):
        st.markdown(plan_markdown)
        
        
    # Store the current plan
    current_plan = {
        "strategy_description": strategy_description,
        "markdown_plan": plan_markdown,
        "session_id": session_id
    }

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('backtesting')
    table.put_item(Item=current_plan)


        
    return {
        "plan_markdown": plan_markdown,
        "session_id": session_id,
        "success": True
    }



@tool
def create_final_report(findings:str, session_id: str):
    """
    Generates the final report
        
    Args:
        session_id: unique id of the agent session
            
    Returns:
        Json array of the plan's identified steps and status
    """

    #dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    #table = dynamodb.Table('backtesting')

    # Get the item
    #response = table.get_item(
    #    Key={'session_id': session_id}
    #)

    #if 'Item' in response:
    #    plan= response['Item'].get('markdown_plan')
    #else:
    #    plan = "Could not find Plan"

        
    # Create a specialized planning agent with detailed instructions
    table_prompt = f"""
Return the following context word for word. If nothing is contained below return "No Context Detected"

{st.session_state['context_test']}


    """

    config = botocore.config.Config(connect_timeout=500, read_timeout=500)
    bedrock = boto3.client('bedrock-runtime' , 'us-east-1', config = config)
        
    user_prompt=f"""Begin"""
    
    message = {
        "role": "user",
        "content": [
            {
                "text": user_prompt
            }
        ]
    }
        
    # Generate the plan
    messages = [message]
    #invoke the model
    response = bedrock.converse(
        modelId= "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        system=[{"text": table_prompt}],
        messages=messages,
        inferenceConfig = {
            "maxTokens": 4096,
            "temperature": 0.1,
        }
    )

    llm_output=response['output']['message']['content'][0]['text']
        
        
    # Store the current plan
    current_step = {
        "session_id": session_id,
        "plan_chart": llm_output
    }

    #write to dynamo
    # Update the item to add the visualization while preserving other attributes

        
    return llm_output
