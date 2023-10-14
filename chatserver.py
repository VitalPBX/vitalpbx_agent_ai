# chatserver.py
import asyncio
import websockets
# Uncomment if you are using a valid domain with SSL
#import ssl
#import logging

# Create a set to store connected WebSocket clients
connected = set()

# Uncomment if you are using a valid domain with SSL
# logging.basicConfig()

#ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

#ssl_cert = "/usr/share/vitalpbx/certificates/your.domain/bundle.pem"
#ssl_key = "/usr/share/vitalpbx/certificates/your.domain/private.pem"

async def echo(websocket, path):
    # Register the WebSocket client.
    print(f"Client {websocket.remote_address} connected.")
    connected.add(websocket)

    try:
        async for message in websocket:
            # Message received from the client
            print(f"Received message from {websocket.remote_address}: {message}")

            # Broadcast the message to all connected clients except the sender
            for conn in connected:
                if conn != websocket:
                    await conn.send(message)
    finally:
        # Unregister the WebSocket client when they disconnect.
        connected.remove(websocket)
        print(f"Client {websocket.remote_address} disconnected.")

# If you are not using SSL, enter the IP of your server; otherwise, enter the domain.
start_server = websockets.serve(echo, 'IP or Domain', 3001)
print("WebSocket server started on ws://IP or Domain:3001")

# Start the WebSocket server
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
