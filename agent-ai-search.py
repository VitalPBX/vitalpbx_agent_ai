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

# Check if SSL is enabled
SSL = "yes"

if SSL == "yes":
    import ssl
    import logging

    logging.basicConfig()
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # Uncomment only if you have a Self-Signed type certificate
    # ssl_context.check_hostname = False  # Disable host name verification
    # ssl_context.verify_mode = ssl.CERT_NONE  # Disable certificate verification

    # You must change the path of your certificates in the following two lines:
    ssl_cert = "/usr/share/vitalpbx/certificates/vitalpbx.home.pem"
    ssl_key = "/usr/share/vitalpbx/certificates/vitalpbx.home.pem"
    ssl_context.load_cert_chain(ssl_cert, keyfile=ssl_key)

# Load environment variables from a .env file
load_dotenv("/var/lib/asterisk/agi-bin/.env")
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_ASSISTANT_ID = os.environ.get('OPENAI_ASSISTANT_ID')
OPENAI_INSTRUCTIONS = os.environ.get('OPENAI_INSTRUCTIONS')

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
                assistant_id=OPENAI_ASSISTANT_ID,
                instructions=OPENAI_INSTRUCTIONS
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
