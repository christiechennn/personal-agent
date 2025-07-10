import os
import boto3
import json
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import tool
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
from langchain_openai import ChatOpenAI
from external.gmail.gmail_client import GmailService
from config.prompt import PROMPT

aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region = os.getenv("AWS_DEFAULT_REGION")
openai_api_key = os.getenv("OPENAI_API_KEY")

bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1", 
                               aws_access_key_id=aws_access_key_id,
                               aws_secret_access_key=aws_secret_key)
bedrock_client = boto3.client("bedrock", region_name="us-east-1", 
                              aws_access_key_id=aws_access_key_id,
                               aws_secret_access_key=aws_secret_key)
boto3.set_stream_logger(name='botocore', level=logging.INFO)

TOOLS = [
    {
        "name": "send_email",
        "description": "Send an email to a specified recipient",
        "input_schema": {
            "type": "object",
            "properties": {
                "recipient": {"type": "string", "description": "Email recipient"},
                "content": {"type": "string", "description": "Email body"}
            },
            "required": ["recipient", "content"]
        }
    }
]

def send_email(recipient: str, content: str) -> str:
    DEFAULT_SENDER = "ymchen217@gmail.com"
    gmail_service = GmailService()

    message = gmail_service.create_message(
            sender=DEFAULT_SENDER,
            to=recipient,
            subject="Test Email from Christie",
            message_text=content
        )

    gmail_service.send_email(message)

    return f"Email sent to {recipient} with message: {content}"
    

def create_agent():
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
    
    tools = [
        send_email
    ]

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    system_message = SystemMessage(content=PROMPT)
    
    agent_executor = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        agent_kwargs={
            "system_message": system_message,
        }
    )
    
    return agent_executor

def run_agent():
    agent_executor = create_agent()
    
    print("Personal AI Agent initialized. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        
        try:
            response = agent_executor.invoke({"input": user_input})
            print(f"AI: {response['output']}")
        except Exception as e:
            print(f"Error: {e}")
            print("AI: I encountered an error processing your request. Please try again.")

def chat_with_claude(messages):
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

        tool_executed, result = parse_and_execute_tool(response_text, messages)
        
        if tool_executed:
            messages.append({
                "role": "assistant",
                "content": f"Tool execution result: {result}"
            })
            
            return chat_with_claude(messages)
            
        return response_text
    except Exception as ex:
        print("Experienced error when calling Claude", str(ex))
        return None

def parse_and_execute_tool(response_text, messages):
    if "<use_tool>" not in response_text:
        return False, response_text
        
    try:
        tool_call_start = response_text.find("<use_tool>") + len("<use_tool>")
        tool_call_end = response_text.find("</use_tool>")
        tool_call_text = response_text[tool_call_start:tool_call_end].strip()
        
        # Parse the tool call
        if "send_email" in tool_call_text:
            # Extract parameters using regex
            import re
            match = re.search(r'send_email\(recipient="([^"]+)", content="([^"]+)"\)', tool_call_text)
            if match:
                recipient = match.group(1)
                content = match.group(2)
                
                result = send_email(recipient, content)
                
                return True, result
                
        return False, response_text
    except Exception as ex:
        print(f"Error parsing or executing tool: {str(ex)}")
        return False, response_text

if __name__ == '__main__':
    load_dotenv()

    # run_agent()

    messages = [
        {
            "role": "user",
            "content": PROMPT
        }
    ]

    print("Claude is ready. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ("exit"):
            break

        # If this is the first user question, combine it with the intro
        if len(messages) == 1:
            messages[0]["content"] += f"\n\n{user_input}"
        else:
            messages.append({"role": "user", "content": user_input})

        response_text = chat_with_claude(messages)

        if response_text:
            print(f"Claude: {response_text}\n")
            messages.append({"role": "assistant", "content": response_text})
        else:
            print("Claude: (no response)\n")
