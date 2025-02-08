from flask import Flask, render_template, Response
import asyncio
import websockets
import threading
import cv2
import numpy as np
import time

app = Flask(__name__)

# Global variable for latest frame
latest_frame = None
frame_lock = threading.Lock()

@app.route('/')
def index():
    """Render HTML page."""
    return render_template('index.html')

async def websocket_server(websocket, path):
    """Receive image frames from WebSocket."""
    global latest_frame
    async for image_bytes in websocket:
        # Decode Image
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Store frame (Thread-Safe)
        with frame_lock:
            latest_frame = frame

# Start WebSocket server in background thread
def start_websocket():
    asyncio.set_event_loop(asyncio.new_event_loop())
    server = websockets.serve(websocket_server, "0.0.0.0", 5000)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()

threading.Thread(target=start_websocket, daemon=True).start()

def generate_stream():
    """Generate MJPEG stream from the latest frame."""
    while True:
        if latest_frame is not None:
            with frame_lock:
                _, jpeg = cv2.imencode('.jpg', latest_frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        time.sleep(0.01)  # Faster frame updates

@app.route('/stream.mjpg')
def stream():
    """MJPEG Video Stream."""
    return Response(generate_stream(), content_type='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
