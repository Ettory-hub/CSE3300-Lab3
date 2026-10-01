import socket
import json
import os

HOST = "0.0.0.0"
PORT = 53533
DB_FILE = "records.json"


def load_records():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}


def save_records(records):
    with open(DB_FILE, "w") as f:
        json.dump(records, f)


records = load_records()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

print(f"Authoritative Server listening on UDP port {PORT}")

while True:
    data, address = sock.recvfrom(4096)
    message = data.decode().strip()

    print("Received:")
    print(message)

    lines = message.splitlines()

    type_value = None
    name = None
    value = None
    ttl = None

    for line in lines:
        parts = line.split()

        for part in parts:
            if part.startswith("TYPE="):
                type_value = part.split("=", 1)[1]
            elif part.startswith("NAME="):
                name = part.split("=", 1)[1]
            elif part.startswith("VALUE="):
                value = part.split("=", 1)[1]
            elif part.startswith("TTL="):
                ttl = part.split("=", 1)[1]

    # Registration request
    if name and value:
        records[name] = {
            "type": type_value or "A",
            "value": value,
            "ttl": ttl or "10"
        }

        save_records(records)

        print(f"Registered {name} -> {value}")
        sock.sendto(b"SUCCESS", address)

    # DNS query
    elif name:
        if name in records:
            record = records[name]

            response = (
                f"TYPE={record['type']}\n"
                f"NAME={name} VALUE={record['value']} TTL={record['ttl']}\n"
            )

            sock.sendto(response.encode(), address)
        else:
            sock.sendto(b"NOT_FOUND", address)

    else:
        sock.sendto(b"ERROR", address)