@staticmethod
def build_message(role:str, input_text:str):
    """
    Build the message to send to the LLM from the input test
    :param input_text: the input text to send to the LLM
    :return: a list containing containing the role, content and user input as text
    """
    return {"role": role, "content": [{"type": "text", "text": input_text}]}