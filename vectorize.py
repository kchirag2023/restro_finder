import os
import pymongo
import time
import json
import streamlit as st
from datetime import datetime
from pymongo import MongoClient, UpdateOne
from openai import AzureOpenAI
from dotenv import load_dotenv
from tenacity import retry, wait_random_exponential, stop_after_attempt

# Load environment variables from .env file
load_dotenv()

# MongoDB connection string and database name
# CONNECTION_STRING = os.environ.get("DB_CONNECTION_STRING")
CONNECTION_STRING = None

print(CONNECTION_STRING )
print("cst")
DATABASE_NAME = "restro"
COMPLETIONS_DEPLOYMENT_NAME =  "gpt-35-turbo"

# Azure OpenAI credentials and deployment names
AOAI_KEY = st.secrets["AOAI_KEY"]
AOAI_ENDPOINT = st.secrets["AOAI_ENDPOINT"]
# AOAI_ENDPOINT = os.environ.get("AOAI_ENDPOINT")
# AOAI_KEY = os.environ.get("AOAI_KEY")
AOAI_API_VERSION = "2024-02-01"
MODEL_NAME = "text-embedding-ada-002"  # Update with the correct model name

# Initialize AzureOpenAI client
ai_client = AzureOpenAI(
    azure_endpoint=AOAI_ENDPOINT,
    api_version=AOAI_API_VERSION,
    api_key=AOAI_KEY,
    azure_deployment=COMPLETIONS_DEPLOYMENT_NAME
)

# MongoDB client and database
client = pymongo.MongoClient(CONNECTION_STRING)
db = client[DATABASE_NAME]




# frontend


# # Initialize an empty list to store chat history
# chat_history = []

# # Function to add messages to chat history
# def add_message(sender, message):
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     chat_history.append({"sender": sender, "message": message, "timestamp": timestamp})

# # Function to display chat history in Streamlit UI
# def chat_history_ui(chat_history):
#     for message in chat_history:
#         if message['sender'] == 'user':
#             st.text_input("You:", value=message['message'], key=message['timestamp'], disabled=True)
#         else:
#             st.text_area("Bot:", value=message['message'], key=message['timestamp'], disabled=True)



st.title("Restaurant Finder")

    # Input field for user's question
user_question = st.text_input("Ask me something:")
    


























# Retry decorator settings
@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def generate_embeddings(text: str):
    '''
    Generate embeddings from string of text using the deployed Azure OpenAI API embeddings model.
    This will be used to vectorize document data and incoming user messages for a similarity search with
    the vector index.
    '''
    response = ai_client.embeddings.create(input=text, model=MODEL_NAME)
    embeddings = response.data[0].embedding
    time.sleep(0.5)  # Rest period to avoid rate limiting on AOAI
    return embeddings

def add_collection_content_vector_field(collection_name: str, data):
    '''
    Add a new field to the collection to hold the vectorized content of each document.
    '''
    collection = db[collection_name]
    bulk_operations = []
    
    for doc in data:
        # remove any previous contentVector embeddings
        if "contentVector" in doc:
            del doc["contentVector"]

        # generate embeddings for the document string representation
        content = json.dumps(doc, default=str)
        content_vector = generate_embeddings(content)  # Assuming generate_embeddings is correctly defined
        
        bulk_operations.append(UpdateOne(
            {"_id": doc["_id"]},
            {"$set": {"contentVector": content_vector}},
            upsert=True
        ))
    
    # execute bulk operations
    collection.bulk_write(bulk_operations)

index_command = {
    'createIndexes': 'restaurants',
    'indexes': [
        {
            'name': 'VectorSearchIndex',
            'key': {
                'contentVector': 'text'
            },
            'weights': {
                'cuisines': 10,  # Example weights; adjust as per relevance
                'avgCostForTwo': 5,
                'editorRating.food': 2,
                'editorRating.service': 2,
                'editorRating.ambience': 1
            }
            # 'cosmosSearchOptions': {
            # 'kind': 'vector-ivf',
            # 'numLists': 1,
            # 'similarity': 'COS',
            # 'dimensions': 1536
            # }
        }
    ]
}















def vector_search(collection_name, query, num_results=3):
    """
    Simulated vector search function for Azure Cosmos DB.
    Replace with actual Azure Cosmos DB querying method.
    """
    client = MongoClient(CONNECTION_STRING)
    db = client[DATABASE_NAME] # Adjust the database name accordingly
    collection = db[collection_name]

    # Simulate a basic query for demonstration
    results = collection.find({ "name": { "$regex": query, "$options": "i" } }).limit(num_results)

    return list(results)

# System prompt template
system_prompt = """
You are a helpful, fun, and friendly assistant for restaurant finder, which provides information about restaurants, their locations, and menus.

Only answer questions related to the information provided about each restaurant.

If you are asked a question that is not in the list, respond with "I don't know."

Restaurant Details:
"""

def rag_with_vector_search(question: str, num_results: int = 3):
    """
    Use the RAG model to generate a prompt using simulated vector search results based on the
    incoming question.
    """
    # Perform vector search (simulated for Azure Cosmos DB)
    results = vector_search("restaurants", question, num_results=num_results)

    # Format product list from simulated vector search results
    product_list = ""
    for result in results:
        product_list += json.dumps(result, indent=4, default=str) + "\n\n"

    # Generate formatted prompt for the LLM with simulated vector search results
    formatted_prompt = system_prompt + product_list

    # Prepare the LLM request
    messages = [
        {"role": "system", "content": formatted_prompt},
        {"role": "user", "content": question}
    ]

    # Call the LLM model to generate the response
    completion = ai_client.chat.completions.create(messages=messages, model=COMPLETIONS_DEPLOYMENT_NAME)
    return completion.choices[0].message.content
print(rag_with_vector_search(user_question, 5))




#done it succefully->created fontend using streamlit.



 # Button to submit user's question
if st.button("Ask"):
        if user_question:
            # Simulate bot response (replace with your actual bot logic)
            bot_answer = rag_with_vector_search(user_question, 5)
            st.write(f"**Answer:** {bot_answer}")
            # add_message("user", user_question)
            # add_message("bot", bot_answer)
        else:
            st.warning("Please enter a question.")

    # Display chat history
# st.subheader("Chat History")
# chat_history_ui(chat_history)


            
            
            
            
            
            

    
    
    
    
# streamlit run vectorize.py