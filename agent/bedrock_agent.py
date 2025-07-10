import os
import boto3
import json
import logging
from typing import Union
from langchain.schema import SystemMessage
from config.prompt import PROMPT
from tools.tool_dispatcher import parse_and_execute_tool
from tools.email_tool import email_tool_description
from agent.roles import Role
from util.utils import build_message

TOOLS = [email_tool_description]

def initialize_bedrock_clients():
    """
    Initialize and return Bedrock clients.
    
    Returns:
        tuple: (bedrock_runtime, bedrock_client) - The initialized Bedrock clients
    """
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    
    bedrock_runtime = boto3.client(
        "bedrock-runtime", 
        region_name=region, 
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_key
    )
    
    bedrock_client = boto3.client(
        "bedrock", 
        region_name=region, 
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_key
    )
    
    return bedrock_runtime, bedrock_client

def chat_with_claude(bedrock_runtime, messages):
    payload = {
        "messages": messages,
        "max_tokens": 500,
        "anthropic_version": "bedrock-2023-05-31",
        "tools": TOOLS
    }

    try:
        response = bedrock_runtime.invoke_model(
            modelId = "anthropic.claude-3-sonnet-20240229-v1:0",
            contentType = "application/json",
            accept = "application/json",
            body = json.dumps(payload)
        )

        response_body = json.loads(response["body"].read())
        print("FULL RESPONSE:", json.dumps(response_body, indent=2))

        response_text = response_body["content"][0]["text"]

        messages.append(build_message(Role.ASSISTANT.value, response_text))

        tool_executed, result = parse_and_execute_tool(response_text)
        
        if tool_executed:
            messages.append(build_message(Role.USER.value, f"<tool_response>{result}</tool_response>"))
        
            return chat_with_claude(bedrock_runtime, messages)
            
        return response_text
    except Exception as ex:
        print("Experienced error when calling Claude", str(ex))
        return None
