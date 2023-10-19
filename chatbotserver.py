import os
import asyncio
import websockets
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
import json
# Uncomment if you are using a valid domain with ssl
#import  ssl
#import logging

# Uncomment if you are using a valid domain with ssl
# logging.basicConfig()

#ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

#ssl_cert = "/usr/share/vitalpbx/certificates/vitalpbx.org/bundle.pem"
#ssl_key = "/usr/share/vitalpbx/certificates/vitalpbx.org/private.pem"

#ssl_context.load_cert_chain(ssl_cert, keyfile=ssl_key)

# Load environment variables from a .env file
load_dotenv('.env')

# Get the path to the database from environment variables
PATH_TO_DATABASE = os.environ.get('PATH_TO_DATABASE')

# Initialize embeddings and vector database
embeddings = OpenAIEmbeddings()
vectordb = Chroma(persist_directory=PATH_TO_DATABASE, embedding_function=embeddings)

# Setup the conversational retrieval chain with OpenAI's chat model and the vector database
pdf_qa = ConversationalRetrievalChain.from_llm(
    ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo'),
    retriever=vectordb.as_retriever(search_kwargs={'k': 6}),
    return_source_documents=True,
    verbose=False
)

# Initialize an empty chat history list
chat_history = []

async def server(websocket, path):
    try:
        data = await websocket.recv()
        payload = json.loads(data)
        query = payload.get('message')
        # Message received from USER
        print(f"USER {websocket.remote_address}: {query}")

        if query:
            result = pdf_qa({"question": query, "chat_history": chat_history})
            response = {'status': 'OK', 'answer': result["answer"]}
            # Message received from ASSISTANT
            print(f"ASSISTANT {websocket.remote_address}: {response}")

        else:
            response = {'status': 'FAIL', 'answer': ''}
        await websocket.send(json.dumps(response))
    except Exception as e:
        print(f"Error occurred: {e}")

# If you are not going to use SSL just enter the IP of your server, otherwise enter the domain.
start_server = websockets.serve(server, '192.168.10.10', 3002)
print("WebSocket server started on ws://192.168.10.10:3002")

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
