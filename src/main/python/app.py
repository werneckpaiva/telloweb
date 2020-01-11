import webbrowser

from flask import Flask, render_template, request
from flask_socketio import SocketIO

from ps_controller import PSController
from tello import Tello

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def main():
    return render_template('main.html')


def refresh_tello_status(tello):
    while True:
        socketio.emit('tello_status', tello.current_status, broadcast=True)
        socketio.sleep(.2)


if __name__ == '__main__':
    print("Starting server at 0.0.0.0:8000")
    print("To watch the video, press triangle and run ffmpeg -i udp://0.0.0.0:11111 -f sdl 'Tello'")
    tello = Tello()
    socketio.start_background_task(refresh_tello_status, tello)
    tello.init()
    controller = PSController(tello)
    webbrowser.open('http://localhost:8000', new=2)
    socketio.run(app, host='0.0.0.0', port=8000)
    tello.stop()
    controller.stop()