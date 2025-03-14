from flask import Flask, render_template
from flask_socketio import SocketIO
from gevent import monkey

monkey.patch_all()

app = Flask(__name__)
socketio = SocketIO(
    app,
    message_queue="redis://172.18.0.100:6379/0",
    cors_allowed_origins="*",
    async_mode="gevent",
)


@app.route("/")
def chat():
    return render_template("chat.html")


@socketio.on("message")
def handle_message(msg):
    socketio.emit("broadcast message", msg)


if __name__ == "__main__":
    try:
        socketio.run(app, host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        print(e)
