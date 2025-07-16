import tiktoken

# For OpenAI models, use 'cl100k_base' for gpt-3.5-turbo, gpt-4, etc.
# You may need to adjust the encoding name for your specific model.
def count_tokens(messages, model_name="gpt-4"):
    """
    Counts the number of tokens in a list of chat messages for OpenAI-compatible models.
    Args:
        messages: List of dicts with 'role' and 'content' keys, e.g. [{"role": "user", "content": "Hello"}]
        model_name: Model name string (default: 'gpt-4')
    Returns:
        int: Total token count
    """
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    num_tokens = 0
    for message in messages:
        # Every message follows <im_start>{role/name}\n{content}<im_end>\n
        num_tokens += 4  # every message metadata
        for key, value in message.items():
            num_tokens += len(encoding.encode(str(value)))
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens
