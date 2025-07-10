from dotenv import load_dotenv
from agent.openai_agent import run_openai_agent
from agent.bedrock_agent import initialize_bedrock_clients, chat_with_claude
from config.prompt import PROMPT
from agent.roles import Role
from util.utils import build_message

def main():
    """
    Main entry point for the personal agent application.
    Loads environment variables and runs the selected agent.
    """
    load_dotenv()

    bedrock_runtime, _ = initialize_bedrock_clients()

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
            messages.append(build_message(Role.USER.value, user_input))

        response_text = chat_with_claude(bedrock_runtime, messages)

        if response_text:
            print(f"Claude: {response_text}\n")
            messages.append(build_message(Role.ASSISTANT.value, response_text))
        else:
            print("Claude: (no response)\n")

if __name__ == '__main__':
    main()
