from flask import Flask, request, jsonify
import socket

app = Flask(__name__)

def fibonacci(n):
    if n < 0:
        raise ValueError("Number must be non-negative")

    a, b = 0, 1

    for _ in range(n):
        a, b = b, a + b

    return a


@app.route("/register", methods=["PUT"])
def register():
    data = request.get_json()

    if not data:
        return "Bad Request", 400

    hostname = data.get("hostname")
    ip = data.get("ip")
    as_ip = data.get("as_ip")
    as_port = data.get("as_port")

    if not hostname or not ip or not as_ip or not as_port:
        return "Bad Request", 400

    message = (
        f"TYPE=A\n"
        f"NAME={hostname} VALUE={ip} TTL=10\n"
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)

    try:
        sock.sendto(message.encode(), (as_ip, int(as_port)))
        response, _ = sock.recvfrom(4096)

        if response.decode().strip() == "SUCCESS":
            return "Registered", 201

        return "Registration Failed", 500

    except Exception as e:
        return str(e), 500

    finally:
        sock.close()


@app.route("/fibonacci", methods=["GET"])
def get_fibonacci():
    number = request.args.get("number")

    try:
        number = int(number)
        result = fibonacci(number)

        return jsonify({
            "number": number,
            "fibonacci": result
        }), 200

    except:
        return "Bad Request", 400


app.run(
    host="0.0.0.0",
    port=9090,
    debug=True
)