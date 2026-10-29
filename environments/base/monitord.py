"""Monitor daemon. Runs as root and records every command the agent's shell reports.

The agent's shell sends one JSON line per command over a Unix socket.
The daemon appends each line, with a timestamp, to a log only root can read.
"""

import json
import os
import socket
import time

SOCKET_DIR = "/run/monitor"
SOCKET_PATH = f"{SOCKET_DIR}/monitor.sock"
LOG_DIR = "/var/log/monitor"
LOG_PATH = f"{LOG_DIR}/commands.jsonl"


def main() -> None:
    os.makedirs(SOCKET_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    os.chmod(LOG_DIR, 0o700)
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    # The agent user must be able to connect, but not read the log.
    os.chmod(SOCKET_PATH, 0o666)
    server.listen()

    while True:
        connection, _ = server.accept()
        with connection, connection.makefile("r") as reader:
            for line in reader:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    record = {"unparsed": line.rstrip("\n")}
                record["received_at"] = time.time()
                with open(LOG_PATH, "a") as log:
                    log.write(json.dumps(record) + "\n")


if __name__ == "__main__":
    main()
