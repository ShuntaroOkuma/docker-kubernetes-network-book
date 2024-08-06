from flask import Flask
import subprocess

app = Flask(__name__)


@app.route("/", methods=["GET"])
def get_ip():
    hostname = (
        subprocess.check_output("hostname").decode(encoding="utf-8").replace("\n", "")
    )
    host_command = [
        "kubectl",
        "get",
        "pods",
        hostname,
        "-o=jsonpath='{.status.hostIP}'",
    ]
    pod_command = ["kubectl", "get", "pods", hostname, "-o=jsonpath='{.status.podIP}'"]
    host_ip = (
        subprocess.check_output(host_command).decode(encoding="utf-8").replace("\n", "")
    )
    pod_ip = (
        subprocess.check_output(pod_command).decode(encoding="utf-8").replace("\n", "")
    )
    return f"pod ip: {pod_ip}, node ip: {host_ip}\n"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
