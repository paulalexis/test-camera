from flask import Flask, render_template, request, Response
import io
import threading
import time

app = Flask(__name__)

latest_frame = None
frame_lock = threading.Lock()

@app.route('/')
def index():
    """Render the main HTML page."""
    return render_template('index.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
    """Receive and store an image from the Raspberry Pi."""
    global latest_frame
    if 'image' in request.files:
        image_file = request.files['image']
        image_bytes = image_file.read()

        # Store the image in a global variable (thread-safe with lock)
        with frame_lock:
            latest_frame = image_bytes
        return 'Image received', 200
    return 'No image received', 400

def generate_stream():
    """Generate MJPEG stream of the latest frame."""
    while True:
        with frame_lock:
            frame = latest_frame
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n'
                   b'Content-Length: %d\r\n\r\n' % len(frame) + frame + b'\r\n')
        else:
            time.sleep(0.001)  # Reduce delay when waiting for frames

@app.route('/stream.mjpg')
def stream():
    """Route to stream the MJPEG."""
    return Response(generate_stream(), 
                    content_type='multipart/x-mixed-replace; boundary=frame',
                    headers={'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)
