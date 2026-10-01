from flask import Flask, request, jsonify
import socket
import requests

app = Flask(__name__)


def query_authoritative_server(hostname, as_ip, as_port):
    message = f"TYPE=A\nNAME={hostname}\n"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)

    try:
        sock.sendto(message.encode(), (as_ip, int(as_port)))
        response, _ = sock.recvfrom(4096)
        return response.decode().strip()
    finally:
        sock.close()


def get_ip_from_response(response):
    if response == "NOT_FOUND":
        return None

    for part in response.split():
        if part.startswith("VALUE="):
            return part.split("=", 1)[1]

    return None


@app.route("/fibonacci", methods=["GET"])
def fibonacci():
    hostname = request.args.get("hostname")
    fs_port = request.args.get("fs_port")
    number = request.args.get("number")
    as_ip = request.args.get("as_ip")
    as_port = request.args.get("as_port")

    if not all([hostname, fs_port, number, as_ip, as_port]):
        return "Bad Request", 400

    try:
        int(number)
        int(fs_port)
        int(as_port)
    except ValueError:
        return "Bad Request", 400

    try:
        dns_response = query_authoritative_server(
            hostname,
            as_ip,
            as_port
        )

        fs_ip = get_ip_from_response(dns_response)

        if not fs_ip:
            return "Hostname not found", 404

        url = f"http://{fs_ip}:{fs_port}/fibonacci?number={number}"

        response = requests.get(url, timeout=5)

        return response.text, response.status_code, {
            "Content-Type": response.headers.get(
                "Content-Type",
                "application/json"
            )
        }

    except Exception as e:
        return jsonify({"error": str(e)}), 500


app.run(
    host="0.0.0.0",
    port=8080,
    debug=True
)