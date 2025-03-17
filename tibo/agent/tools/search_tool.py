import openai
from ...utils import OPENAI_API_KEY

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def web_search(query: str) -> str:
    """Perform a web search using OpenAI's API with function calling."""
    response = client.chat.completions.create(
        model="gpt-4o-mini-search-preview",
        messages=[
            {
                "role": "user",
                "content": query
            }
        ],
    )
    return response.choices[0].message.content


