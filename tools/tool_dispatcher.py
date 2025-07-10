from tools.email_tool import parse_and_send_email

def parse_and_execute_tool(response_text):
    if "<use_tool>" not in response_text:
        return False, response_text

    try:
        start = response_text.index("<use_tool>") + len("<use_tool>")
        end = response_text.index("</use_tool>")
        tool_call_text = response_text[start:end].strip()

        if "send_email" in tool_call_text:
            return parse_and_send_email(tool_call_text)

        return False, response_text
    except Exception as e:
        print(f"Error parsing/executing tool: {e}")
        return False, response_text