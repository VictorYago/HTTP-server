import socket

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
        "body": headers
    }

def make_response(status: int, body: dict) -> str:
    status_text = {
        200: "OK",
        201: "Created",
        404: "Not Found",
        400: "Bad Request"
    }
    payload = json.dumps(body, ensure_ascii=False)
    return (
        f"HTTP/1.1 {status} {status_text.get(status, '')}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(payload.encode())}\r\n"
        f"\r\n"
        f"{payload}"
    )

def handle(req: dict) -> str:
    global next_id
    method = req["method"]
    path = req["path"]

    #GET /tasks
    if method == "GET" and path == "/tasks":
        return make_response(200, list(tasks.values()))
    
    #GET /tasks/id
    if method == "GET" and path.startswith("/tasks/"):
        tid = path.split("/")[-1]
        if tid not in tasks:
            return make_response(404, {"erro":"Tarefa não encontrada"})
        return make_response(200, tasks[tid])
    
    # POST /tasks → cria
    if method == "POST" and path == "/tasks":
        try:
            data = json.loads(req["body"])
        except Exception:
            return make_response(400, {"erro": "Body JSON inválido"})
        tid = str(next_id)
        next_id += 1
        tasks[tid] = {"id": tid, "titulo": data.get("titulo", ""), "feita": False}
        return make_response(201, tasks[tid])

    # PUT /tasks/{id} → atualiza completo
    if method == "PUT" and path.startswith("/tasks/"):
        tid = path.split("/")[-1]
        if tid not in tasks:
            return make_response(404, {"erro": "Tarefa não encontrada"})
        data = json.loads(req["body"])
        tasks[tid] = {"id": tid, **data}
        return make_response(200, tasks[tid])

    # DELETE /tasks/{id} → remove
    if method == "DELETE" and path.startswith("/tasks/"):
        tid = path.split("/")[-1]
        if tid not in tasks:
            return make_response(404, {"erro": "Tarefa não encontrada"})
        deleted = tasks.pop(tid)
        return make_response(200, {"deletada": deleted})

    return make_response(404, {"erro": "Rota não encontrada"})

#criar o socket TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
server.listen(5)

print(f"Servidor rodando em https://{HOST}:{PORT}")

while True:
    conn, addr = server.accept()
    print(f"Conexão de {addr}")

    data = conn.recv(4096).decode()
    #print("--- REQUEST RAW ---")
    #print(data.decode())
    req = parse_request(data)
    print(f"{req['method']} {req['path']}")
    print("Headers:", req['headers'])
    print("Body:", req['body'])

    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/plain\r\n"
        "\r\n"
        "OK!"
    )

    conn.sendall(response.encode())
    conn.close()