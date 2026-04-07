import socket

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

    data = conn.recv(1024)
    print("--- REQUEST RAW ---")
    print(data.decode())

    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/plain\r\n"
        "\r\n"
        "Ola, HTTP!"
    )

    conn.sendall(response.encode())
    conn.close()