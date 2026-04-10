import socket
import json
import threading
from typing import Callable, Dict

HOST = "localhost"
PORT = 8080

tasks = {}
next_id = 1

def parse_request(raw: str) -> dict:
    lines = raw.split("\r\n")
    method, path, version = lines[0].split(" ")
    headers = {}

    i = 1
    while i < len(lines) and lines[i] != "":
        key, _, value = lines[i].partition(": ")
        headers[key] = value
        i += 1

    body = "\r\n".join(lines[i+1:]) if i + 1 < len(lines) else ""

    return {
        "method": method,
        "path": path,
        "version": version,
        "headers": headers,
        "body": body
    }

_STATUS_TEXT = {
        200: "OK",
        201: "Created",
        204: "No Content",
        400: "Bad Request",
        404: "Not Found",
        405: "Method not Allowed",
        500: "Internal Server Error"
    }

def make_response(status: int, body: dict) -> str:
    
    payload = json.dumps(body, ensure_ascii=False)
    return (
        f"HTTP/1.1 {status} {_STATUS_TEXT.get(status, '')}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(payload.encode())}\r\n"
        f"\r\n"
        f"{payload}"
    )

Handler = Callable[[dict], str] 

class HTTPServer:
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self._routes: Dict[tuple, Handler] = {}

    #Routes
    def route(self, method: str, path: str):
        # """Decorator: @app.route("GET", "/tasks")"""
        def decorator(fn: Handler):
            self._routes[(method.upper(), path)] = fn
            return fn
        return decorator
    
    def get(self,    path): return self.route("GET",    path)
    def post(self,   path): return self.route("POST",   path)
    def put(self,    path): return self.route("PUT",    path)
    def delete(self, path): return self.route("DELETE", path)

    def dispatch(self, req: dict) -> str:
        method = req["method"]
        path = req["path"]

        handler = self._routes.get((method, path))
        if handler:
            return handler(req)
        
        for (m, p), fn in self._routes.items():
            if m == method and p.endswith("/*") and path.startswith(p[:-2]):
                return fn(req)
        return make_response(404, {"erro": "Rota não encontrada"})
    
    def handle_connection(self, conn: socket.socket, addr):
        try:
            raw = conn.recv(4096).decode()
            req = parse_request(raw)

            print(f"[{addr[0]}] {req['method']} {req['path']}")

            response = self.dispatch(req)
            conn.sendall(response.encode())
        except Exception as e:
            conn.sendall(make_response(500, {"erro": str(e)}).encode())
        finally:
            conn.close()


    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f"Servidor rodando em http://{self.host}:{self.port}")

        while True:
            conn, addr = server.accept()
            t = threading.Thread(
                target = self.handle_connection,
                args = (conn, addr),
                daemon = True
            )
            t.start()
            
