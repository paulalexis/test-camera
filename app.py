from flask import Flask, render_template
import asyncio
import websockets

app = Flask(__name__)

@app.route('/')
def index():
    """Render HTML page."""
    return render_template('index.html')

async def websocket_server(websocket, path):
    """Handle WebSocket connections."""
    while True:
        try:
            message = await websocket.recv()
            print(f"Received: {message}")
            await websocket.send(f"Echo: {message}")
        except websockets.ConnectionClosed:
            break

async def start_websocket():
    """Start WebSocket Server."""
    server = await websockets.serve(websocket_server, "0.0.0.0", 443)  # Run on Port 443
    await server.wait_closed()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_websocket())  # Start WebSocket Server
    app.run(host='0.0.0.0', port=10000, threaded=True)  # Flask Server on Port 10000
