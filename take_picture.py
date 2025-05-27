import cv2
import qrcode
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import os
import socket
from PIL import Image
import time

# Step 1: Take a picture using OpenCV
def capture_image(filename="image.jpg"):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera could not be opened.")
        return
    print("Press SPACE to capture the image...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Camera - Press SPACE to Capture", frame)
        key = cv2.waitKey(1)
        if key == 32:  # SPACE key
            cv2.imwrite(filename, frame)
            print(f"Image saved as {filename}")
            break

    cap.release()
    cv2.destroyAllWindows()

# Step 2: Start local server to serve the image
def start_server(port=8000):
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(("", port), handler)
    print(f"Serving at http://{get_local_ip()}:{port}")
    httpd.serve_forever()

# Get the local IP address (for phones to connect over same Wi-Fi)
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to connect; just get IP
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

# Step 3: Generate QR code pointing to the local image
def generate_qr(url, qr_filename="qr.png"):
    qr = qrcode.make(url)
    qr.save(qr_filename)
    print(f"QR Code saved as {qr_filename}")
    img = Image.open(qr_filename)
    img.show()

# Step 4: Auto-delete after 30 seconds
def delete_files_after_delay(image_file, qr_file, delay=60):
    time.sleep(delay)
    for file in [image_file, qr_file]:
        if os.path.exists(file):
            os.remove(file)
            print(f"{file} deleted.")
    print("Files removed after timeout.")

# === MAIN FLOW ===
image_filename = "image.jpg"
qr_filename = "qr.png"

capture_image(image_filename)

# Start server in background
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

# Create link using local IP
local_url = f"http://{get_local_ip()}:8000/{image_filename}"
generate_qr(local_url, qr_filename)

# Start deletion countdown in background
cleanup_thread = threading.Thread(
    target=delete_files_after_delay,
    args=(image_filename, qr_filename),
    daemon=True
)
cleanup_thread.start()

input("Scan the QR code to view the image. Press ENTER to end the program.\n")
