#!/usr/bin/env python3
# client.py
"""
Cliente simple:
- se conecta al servidor
- envía {"payload": ...} como JSON por línea
- espera ack {"status":"enqueued","task_id":...}
- luego espera {"task_id":...,"result":...}
"""

import socket
import sys
import json
import time

HOST = "127.0.0.1"
PORT = 5000
RECV_TIMEOUT = 30.0


def send_json(conn: socket.socket, obj: dict):
    """Enviar objeto JSON terminado en \n."""
    conn.sendall((json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8"))


def recv_lines(conn: socket.socket):
    """Generador que yield líneas completas (decodificadas)."""
    buf = b""
    while True:
        chunk = conn.recv(4096)
        if not chunk:
            if buf:
                yield buf.decode("utf-8")
            return
        buf += chunk
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            yield line.decode("utf-8")


def run_client(payload):
    """Conecta, envía payload y espera resultado para esa tarea."""
    conn = socket.create_connection((HOST, PORT))
    try:
        send_json(conn, {"payload": payload})
        gen = recv_lines(conn)
        start = time.time()
        task_id = None
        # esperar ack
        for line in gen:
            obj = json.loads(line)
            if obj.get("status") == "enqueued" and obj.get("task_id"):
                task_id = obj["task_id"]
                print(f"[client] tarea encolada id={task_id}.")
                print("Esperando resultado...")
                break
            print("[client] msg:", obj)
            if time.time() - start > RECV_TIMEOUT:
                print("[client] timeout esperando ack")
                return
        if not task_id:
            print("[client] no recibí ack. saliendo.")
            return
        # esperar resultado
        for line in gen:
            obj = json.loads(line)
            if obj.get("task_id") == task_id:
                print("[client] resultado recibido:", obj.get("result"))
                return
            print("[client] recibido mensaje no esperado:", obj)
            if time.time() - start > RECV_TIMEOUT:
                print("[client] timeout esperando resultado")
                return
        print("[client] conexión cerrada antes de recibir resultado.")
    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        try:
            payload = json.loads(sys.argv[1])
        except Exception:
            payload = sys.argv[1]
    else:
        s = input("Ingrese payload (JSON o texto): ").strip()
        try:
            payload = json.loads(s)
        except Exception:
            payload = s
    run_client(payload)
