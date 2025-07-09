from strands import Agent
from strands.models import BedrockModel
from strands_tools import calculator
import streamlit as st
import agent_visualizer 
from research_tools import search_web
from stock_tools import get_daily_historical_stock_data, get_stock_quote, get_earnings_transcript, get_earnings_calendar, get_company_overview
from datetime import datetime
from planning_agent import create_plan

#get the current time and date in human readbale format - using a pyhton library

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
current_date = now.strftime("%Y-%m-%d")

bedrock_model = BedrockModel(
        model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",  # Specify the model ID
        temperature=0.7,  # Control randomness (0.0 to 1.0)
        top_p=0.9,  # Control diversity
        max_tokens=2000,  # Maximum response length
        region_name="us-west-2"  # AWS region where you have model access
    )

# Simple step tracking
current_step = 0
accumulated_text = ""
shown_tools = set()

def custom_callback_handler(**kwargs):
    global current_step, accumulated_text, shown_tools
    
    # Handle complete tool calls from message
    if "message" in kwargs:
        message = kwargs["message"]
        if message.get("role") == "assistant" and "content" in message:
            for content in message["content"]:
                # Show any accumulated text first
                if "text" in content and accumulated_text:
                    st.write(f"**Agent:** {accumulated_text}")
                    accumulated_text = ""
                    current_step += 1
                
                # Show tool calls
                if "toolUse" in content:
                    tool_use = content["toolUse"]
                    tool_id = tool_use.get("toolUseId")
                    if tool_id not in shown_tools:
                        shown_tools.add(tool_id)
                        st.info(f"🔧 **{tool_use['name']}** called with: {tool_use['input']}")
                        current_step += 1
        
        # Handle tool results
        elif message.get("role") == "user" and "content" in message:
            for content in message["content"]:
                if "toolResult" in content:
                    result = content["toolResult"]
                    if result.get("status") == "success":
                        result_text = result["content"][0]["text"] if result.get("content") else "Success"
                        if len(result_text) > 200:
                            result_text = result_text[:200] + "..."
                        st.success(f"📊 Tool result: {result_text}")
                        current_step += 1
    
    # Handle streaming response (just accumulate)
    elif "data" in kwargs and kwargs['data']:
        accumulated_text += kwargs['data']


# Reset
current_step = 0
accumulated_text = ""
shown_tools = set()

#Streamlit user interactions

user_question = st.text_input("Ask a question:", "Has amazon been trending up or down recently? Any insights as to why?")

go = st.button("Go")


st.session_state['context_test'] = "I AM TESTING MY SESSION STATE"


if go:

# Create agent
    agent = Agent(
        tools=[search_web, get_daily_historical_stock_data, get_stock_quote, get_earnings_transcript, get_earnings_calendar, get_company_overview, create_plan],
        callback_handler=custom_callback_handler,
        model=bedrock_model,
        system_prompt=f"""
The Current Time and Date is: {current_date}  {current_time}

FINANCIAL RESEARCH AGENT
You are an expert financial analyst tasked with conducting rigorous, multi-source research to answer complex financial questions. Your core objectives:
RESEARCH APPROACH:

Always Create a plan first

Synthesize data from multiple authoritative sources to build comprehensive analyses
Validate findings through cross-referencing and triangulation
Distinguish between correlation and causation in financial relationships
Account for market volatility, regulatory changes, and macroeconomic factors

ANALYTICAL RIGOR:

Quantify uncertainty and provide confidence intervals where appropriate
Run probabilistic models to assess risk scenarios and potential outcomes
Identify key assumptions and stress-test conclusions against alternative scenarios
Present both bull and bear cases with supporting evidence

OUTPUT STANDARDS:

Lead with clear, actionable insights supported by data
Cite specific sources and methodologies used
Highlight potential biases, limitations, and conflicting evidence
Structure findings from high-level conclusions to detailed supporting analysis

CRITICAL THINKING:

Question conventional wisdom and market consensus when evidence suggests otherwise
Consider second and third-order effects of financial events
Evaluate information quality and potential conflicts of interest in sources
Maintain objectivity regardless of market sentiment or popular narratives

Deliver precise, evidence-based insights that enable informed financial decision-making.
"""
    )

    result = agent(user_question)

    # Show final accumulated text if any
    if accumulated_text:
        st.markdown(f"**Agent:** {accumulated_text}")

    st.markdown(result)

    #display metrics and vsiualizations in sidebar
    agent_visualizer.show_agent_summary_sidebar(result)
