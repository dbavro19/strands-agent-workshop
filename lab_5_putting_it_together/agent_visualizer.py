"""
Agent Flow Visualizer Module
Save this as: agent_visualizer.py
"""

import streamlit as st

def safe_duration(duration):
    """Safely handle None duration values"""
    return duration if duration is not None else 0.0

def calculate_total_duration(metrics):
    """Calculate total duration using accumulated_metrics.latencyMs or traces"""
    
    # First try accumulated_metrics.latencyMs (most accurate)
    accumulated_metrics = metrics.get('accumulated_metrics', {})
    latency_ms = accumulated_metrics.get('latencyMs', 0)
    if latency_ms > 0:
        return latency_ms / 1000.0
    
    # Fallback: calculate from traces
    traces = metrics.get('traces', [])
    if not traces:
        return 0.0
    
    # Find earliest start and latest end
    earliest_start = None
    latest_end = None
    
    for trace in traces:
        start_time = trace.get('start_time')
        end_time = trace.get('end_time')
        
        if start_time:
            if earliest_start is None or start_time < earliest_start:
                earliest_start = start_time
        
        if end_time:
            if latest_end is None or end_time > latest_end:
                latest_end = end_time
    
    if earliest_start and latest_end:
        return latest_end - earliest_start
    
    return safe_duration(metrics.get('total_duration', 0))

def show_agent_summary_sidebar(result):
    """
    Display simplified agent analysis in sidebar
    """
    with st.sidebar:
        st.title("🤖 AGENT ANALYSIS")
        
        metrics = result.metrics.get_summary()
        
        # Overview Section
        st.subheader("📊 Overview")
        
        col1, col2 = st.columns(2)
        with col1:
            # Use more accurate duration calculation
            total_duration = calculate_total_duration(metrics)
            st.metric("Duration", f"{total_duration:.2f}s")
        
        with col2:
            st.metric("Cycles", metrics.get('total_cycles', 0))
        
        # Token usage
        accumulated_usage = metrics.get('accumulated_usage', {})
        total_tokens = accumulated_usage.get('totalTokens', 0)
        input_tokens = accumulated_usage.get('inputTokens', 0)
        output_tokens = accumulated_usage.get('outputTokens', 0)
        
        st.metric("Total Tokens", total_tokens)
        if total_tokens > 0:
            st.write(f"**Input:** {input_tokens} | **Output:** {output_tokens}")
        
        # Tool count
        tool_count = len(metrics.get('tool_usage', {}))
        st.metric("Tools Used", tool_count)
        
        # Execution Traces Section
        st.subheader("📋 Execution Traces")
        create_detailed_trace(metrics.get('traces', []))
        
        # Raw JSON Section
        st.subheader("📄 Full Stack Trace")
        with st.expander("View Complete JSON", expanded=False):
            st.json(metrics)

def create_detailed_trace(traces):
    """Create detailed execution trace view with proper timing"""
    
    if not traces:
        st.warning("No trace data")
        return
    
    for i, trace in enumerate(traces):
        cycle_name = trace.get('name', f'Cycle {i+1}')
        
        # Calculate cycle duration more accurately
        start_time = trace.get('start_time')
        end_time = trace.get('end_time')
        
        if start_time and end_time:
            cycle_duration = end_time - start_time
        elif trace.get('duration'):
            cycle_duration = safe_duration(trace.get('duration'))
        else:
            # Calculate from children if no direct duration
            children = trace.get('children', [])
            cycle_duration = 0
            for child in children:
                child_start = child.get('start_time')
                child_end = child.get('end_time')
                if child_start and child_end:
                    child_dur = child_end - child_start
                    cycle_duration = max(cycle_duration, child_dur)
        
        with st.expander(f"{cycle_name} ({cycle_duration:.3f}s)", expanded=True):
            children = trace.get('children', [])
            
            for child in children:
                child_name = child.get('name', 'Unknown')
                
                # Calculate child duration properly
                child_start = child.get('start_time')
                child_end = child.get('end_time')
                
                if child_start and child_end:
                    child_duration = child_end - child_start
                elif child.get('duration'):
                    child_duration = safe_duration(child.get('duration'))
                else:
                    child_duration = 0.0
                
                st.write(f"**{child_name}** - {child_duration:.3f}s")
                
                # Show key message info
                if child.get('message'):
                    message = child['message']
                    content = message.get('content', [])
                    
                    for content_item in content:
                        if 'toolUse' in content_item:
                            tool_use = content_item['toolUse']
                            st.code(f"{tool_use['name']}: {tool_use['input']}")
                        elif 'toolResult' in content_item:
                            result_content = content_item['toolResult'].get('content', [])
                            if result_content:
                                result_text = result_content[0].get('text', 'No result')
                                st.success(f"Result: {result_text}")
                        elif 'text' in content_item:
                            # Show first part of text responses
                            text = content_item['text']
                            if len(text) > 100:
                                st.write(f"*Response:* {text[:100]}...")
                            else:
                                st.write(f"*Response:* {text}")
                
                st.write("---")