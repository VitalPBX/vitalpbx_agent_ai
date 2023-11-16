#!/usr/bin/env python3

import time
import os
import sys
import asyncio
import websockets
import markdown
from dotenv import load_dotenv
import openai
from openai import OpenAI
import json

SSL = "yes"
if SSL == "yes":
    import  ssl
    import logging
    logging.basicConfig()
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # You must change the path of your certificates in the following two lines:
    ssl_cert = "/usr/share/vitalpbx/certificates/vitalpbx.home.pem"
    ssl_key = "/usr/share/vitalpbx/certificates/vitalpbx.home.pem"
    ssl_context.load_cert_chain(ssl_cert, keyfile=ssl_key)

# Load environment variables from a .env file
load_dotenv("PATH_TO_.ENV_FILE/.env")
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

client = OpenAI()
thread = client.beta.threads.create()

# Files can also be added to a Message in a Thread. These files are only accessible within this specific thread. 
# After having uploaded a file, you can pass the ID of this File when creating the Message.

async def server(websocket, path):
    try:
        data = await websocket.recv()
        payload = json.loads(data)
        query = payload.get('message')
        # Message received from USER
        print(f"USER {websocket.remote_address}: {query}")

        if query:
            message = client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=query
            )

            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id="asst_3787z2CDX12ZdoIzrN2S2Fzn",
                instructions="Please address the user as Dear Customer. The user has a premium account."
            )

            runStatus = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

            # Wait for Assistant to respond
            while runStatus.status != "completed":
                time.sleep(1)
                runStatus = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            print(runStatus.status)

            # Get the last message
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )

            html = markdown.markdown(messages.data[0].content[0].text.value)
            response = {'status': 'OK', 'answer': html}

            print(html)

            # Message received from ASSISTANT
            print(f"ASSISTANT {websocket.remote_address}: {response}")

        else:
            response = {'status': 'FAIL', 'answer': ''}
        await websocket.send(json.dumps(response))

    except Exception as e:
        print(f"Error occurred: {e}")

# Print the last message
# print(f'Assistant: {messages.data[0].content[0].text.value}')

if SSL == "yes":
    start_server = websockets.serve(server, '0.0.0.0', 3002, ssl=ssl_context)
    print("WebSocket server started on wss://0.0.0.0:3002")
else:
    start_server = websockets.serve(server, '0.0.0.0', 3002)
    print("WebSocket server started on ws://0.0.0.0:3002")

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
