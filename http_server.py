import socket

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

HOST = "localhost"
PORT = 8080

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