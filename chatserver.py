#!/usr/bin/env python3
import asyncio
import websockets
import markdown

SSL = "yes"
if SSL == "yes":
    import  ssl
    import logging
    logging.basicConfig()
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.check_hostname = False  # Disable host name verification
    ssl_context.verify_mode = ssl.CERT_NONE  # Disable certificate verification
    # You must change the path of your certificates in the following two lines:
    ssl_cert = "/usr/share/vitalpbx/certificates/vitalpbx.home.pem"
    ssl_key = "/usr/share/vitalpbx/certificates/vitalpbx.home.pem"
    ssl_context.load_cert_chain(ssl_cert, keyfile=ssl_key)

# Create a set to store connected WebSocket clients
connected = set()

async def echo(websocket, path):
    # Register the WebSocket client.
    print(f"Client {websocket.remote_address} connected.")
    connected.add(websocket)

    try:
        async for message in websocket:
            # Message received from the client
            html = markdown.markdown(message)
            print(f"Received message from {websocket.remote_address}: {html}")

            # Broadcast the message to all connected clients except the sender
            for conn in connected:
                if conn != websocket:
                    await conn.send(html)
    finally:
        # Unregister the WebSocket client when they disconnect.
        connected.remove(websocket)
        print(f"Client {websocket.remote_address} disconnected.")

if SSL == "yes":
    start_server = websockets.serve(echo, '0.0.0.0', 3001, ssl=ssl_context)
    print("WebSocket server started on wss://0.0.0.0:3001")
else:
    start_server = websockets.serve(echo, '0.0.0.0', 3001)
    print("WebSocket server started on ws://0.0.0.0:3001")

# Start the WebSocket server
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
