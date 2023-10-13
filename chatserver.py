# chatserver.py
import asyncio
import websockets
# Uncomment if you are using a valid domain with ssl
#import  ssl
#import logging

connected = set()

# Uncomment if you are using a valid domain with ssl
# logging.basicConfig()

#ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

#ssl_cert = "/usr/share/vitalpbx/certificates/vitalpbx.org/bundle.pem"
#ssl_key = "/usr/share/vitalpbx/certificates/vitalpbx.org/private.pem"

async def echo(websocket, path):
    # Register.
    print(f"Client {websocket.remote_address} connected.")
    connected.add(websocket)

    try:
        async for message in websocket:
            # Message received from client
            print(f"Received message from {websocket.remote_address}: {message}")

            for conn in connected:
                if conn != websocket:
                    await conn.send(message)
    finally:
        # Unregister.
        connected.remove(websocket)
        print(f"Client {websocket.remote_address} disconnected.")

# If you are not going to use SSL just enter the IP of your server, otherwise enter the domain.
start_server = websockets.serve(echo, '192.168.10.10', 3001)
print("WebSocket server started on ws://192.168.10.10:3001")

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
