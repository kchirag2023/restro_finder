import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()
chatClient = AzureOpenAI(
  azure_endpoint=os.getenv("AOAI_ENDPOINT"), 
  api_key=os.getenv("AOAI_KEY"),  
  api_version="2024-02-01"
)
chatResponse = chatClient.chat.completions.create(
    model="gpt-35-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful, fun and friendly sales assistant for Cosmic Works, a bicycle and bicycle accessories store."},
        {"role": "user", "content": "Do you sell bicycles?"},
        {"role": "assistant", "content": "Yes, we do sell bicycles. What kind of bicycle are you looking for?"},
        {"role": "user", "content": "what is in the menu of karim's?"}
    ]
)

print(chatResponse.choices[0].message.content)