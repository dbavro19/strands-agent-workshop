from strands import Agent, tool
import boto3
import requests
import streamlit as st 


@tool(name="search_web", description="Searches the web based on the submitted query: Useful for real time and general search topics")
def search_web(query: str) -> str:
    """Search the web using Brave Search API"""
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
       "Accept": "application/json",
       "X-Subscription-Token": "BSAiV8QEIQVYvl0a2oAiiIM8brEiITX"
   }
    params = {
        "q": query,
        "count": 10
   }
    response = requests.get(url, headers=headers, params=params)



    response.raise_for_status()

    return f" results: {response.json()}"

    return {
            "status": "success",
            "content": [ {
                "json": response.json(),
            }]
        }
   


@tool(name="knowledge_base_search", description="Retrieves relevant document content based on the users questions via semantic search. Must include the fund/organization name")
def knowledge_base_search_v2(user_question: str, fund_name: str) -> str:
    """
    Retrieves relevant document content based on the users questions via semantic search. Must include the organization/fund name
    
    Args:
        user_question: The most recent Question the user has asked
        fund_name: name of the relevant fund / organization pertaining to the question
        
    Returns:
        A relevant answer based on the relevant documents 
    """

    import requests
   
    




