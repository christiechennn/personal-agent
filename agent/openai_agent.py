import os
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
from tools.email_tool import send_email

def create_openai_agent(prompt):
    """
    Create and initialize an OpenAI agent with the specified prompt and tools.
    
    Args:
        prompt (str): The system prompt for the agent
        
    Returns:
        AgentExecutor: The initialized agent executor
    """
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
    
    tools = [
        send_email
    ]

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    system_message = SystemMessage(content=prompt)
    
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

def run_openai_agent(prompt):
    """
    Run the OpenAI agent in an interactive loop.
    
    Args:
        prompt (str): The system prompt for the agent
    """
    agent_executor = create_openai_agent(prompt)
    
    print("Personal AI Agent (OpenAI) initialized. Type 'exit' to quit.")
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
