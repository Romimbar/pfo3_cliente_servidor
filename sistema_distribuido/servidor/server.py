#!/usr/bin/env python3
# server.py
"""
Servidor sencillo:
- acepta conexiones TCP
- cliente envía JSON por línea: {"payload": ...}
- el servidor asigna task_id y encola la tarea
- pool de workers (hilos) procesa tareas y pone resultados en result_q
- dispatcher envía resultado al cliente que originó la tarea
"""

import socket
import threading
import json
import uuid
import time
from queue import Queue, Empty
from typing import Dict

HOST = "0.0.0.0"
PORT = 5000
WORKER_COUNT = 4
TASK_QUEUE_TIMEOUT = 0.5


def send_json(conn: socket.socket, obj: dict):
    """Enviar un objeto JSON terminado en \n."""
    data = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
    conn.sendall(data)


def recv_lines(conn: socket.socket):
    """Generador: devuelve líneas (decodificadas) terminadas en \n."""
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


def worker(task_q: Queue, result_q: Queue, wid: int):
    """Worker: consume tareas, procesa y coloca resultados."""
    print(f"[worker-{wid}] started")
    while True:
        try:
            task = task_q.get(timeout=1)
        except Empty:
            continue
        try:
            payload = task["payload"]
            # Simular trabajo: op simple "square"
            time.sleep(0.3)
            if isinstance(payload, dict) and payload.get("op") == "square":
                n = payload.get("n", 0)
                result_value = n * n
            else:
                result_value = {"echo": payload}
            result = {
                "task_id": task["task_id"],
                "result": result_value,
                "worker": wid,
                "started_at": task.get("started_at"),
                "finished_at": time.time(),
            }
            result_q.put(result)
        except Exception as e:
            result_q.put({"task_id": task.get("task_id"),
                          "result": {"error": str(e)}})


class TaskServer:
    """Servidor que gestiona cola de tareas y conexiones de clientes."""

    def __init__(self, host, port, workers=4):
        self.host = host
        self.port = port
        self.task_q = Queue()
        self.result_q = Queue()
        self.task_to_conn: Dict[str, socket.socket] = {}
        self.lock = threading.Lock()
        self.workers = []
        self.worker_count = workers
        self.should_stop = threading.Event()

    def start_workers(self):
        """Iniciar threads worker."""
        for i in range(self.worker_count):
            t = threading.Thread(
                target=worker,
                args=(self.task_q, self.result_q, i + 1),
                daemon=True,
            )
            t.start()
            self.workers.append(t)
        print(f"[server] {len(self.workers)} worker threads started")

    def start_dispatcher(self):
        """Inicia thread que despacha resultados a clientes."""
        t = threading.Thread(target=self._dispatcher_loop, daemon=True)
        t.start()

    def _dispatcher_loop(self):
        """Lee result_q y envía resultados al cliente correspondiente."""
        print("[dispatcher] started")
        while not self.should_stop.is_set():
            try:
                res = self.result_q.get(timeout=TASK_QUEUE_TIMEOUT)
            except Empty:
                continue
            if not res:
                continue
            task_id = res.get("task_id")
            conn = None
            with self.lock:
                conn = self.task_to_conn.pop(task_id, None)
            if conn:
                try:
                    send_json(
                        conn,
                        {
                            "task_id": task_id,
                            "result": res.get("result"),
                        },
                    )
                except Exception:
                    try:
                        conn.close()
                    except Exception:
                        pass
                    print("[dispatcher] failed to send result to client")
            else:
                print(f"[dispatcher] client not present for task {task_id}")

    def handle_client(self, conn: socket.socket, addr):
        """Loop por cliente: recibe tareas y encola."""
        print(f"[client] connected {addr}")
        try:
            for line in recv_lines(conn):
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    send_json(conn, {"error": "invalid json"})
                    continue
                payload = data.get("payload", data)
                task_id = str(uuid.uuid4())
                now = time.time()
                task = {"task_id": task_id,
                        "payload": payload,
                        "started_at": now}
                with self.lock:
                    self.task_to_conn[task_id] = conn
                self.task_q.put(task)
                send_json(conn, {"status": "enqueued",
                                 "task_id": task_id})
            print(f"[client] {addr} closed connection")
        except Exception as e:
            print(f"[client] {addr} error: {e}")
        finally:
            with self.lock:
                to_remove = [tid for tid, c in self.task_to_conn.items()
                             if c is conn]
                for tid in to_remove:
                    self.task_to_conn.pop(tid, None)
            try:
                conn.close()
            except Exception:
                pass
            print(f"[client] {addr} cleaned up")

    def serve_forever(self):
        """Arranca el servidor TCP y acepta conexiones."""
        self.start_workers()
        self.start_dispatcher()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(16)
        print(f"[server] listening on {self.host}:{self.port}")
        try:
            while not self.should_stop.is_set():
                s.settimeout(1.0)
                try:
                    conn, addr = s.accept()
                except socket.timeout:
                    continue
                t = threading.Thread(target=self.handle_client,
                                     args=(conn, addr), daemon=True)
                t.start()
        except KeyboardInterrupt:
            print("[server] interrupted")
        finally:
            print("[server] shutting down")
            self.should_stop.set()
            try:
                s.close()
            except Exception:
                pass


if __name__ == "__main__":
    srv = TaskServer(HOST, PORT, WORKER_COUNT)
    srv.serve_forever()
