import socket
import threading

# Configurações do servidor
HOST = '127.0.0.1'
PORT = 5000

# Função para lidar com conexões de clientes
def handle_client(conn, addr):
    print(f"Conexão estabelecida com {addr}")
    
    while True:
        # Recebe os dados do cliente
        data = conn.recv(1024)
        if not data:
            break
        
        # Interpreta a mensagem recebida
        mensagem = data.decode()
        tipo, conteudo = interpretar_mensagem(mensagem)
        
        if tipo == "DADOS":
            print(f"Recebido de {addr}: {conteudo}")
            resposta = criar_mensagem("ACK", "Recebido com sucesso")
            conn.sendall(resposta.encode())  # Responde ao cliente com um ACK
        
    conn.close()
    print(f"Conexão encerrada com {addr}")

# Função para criar uma mensagem
def criar_mensagem(tipo, conteudo):
    return f"{tipo}:{conteudo}"

# Função para interpretar uma mensagem
def interpretar_mensagem(mensagem):
    partes = mensagem.split(":", 1)
    return partes[0], partes[1] if len(partes) > 1 else ""

# Inicialização do servidor
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Servidor escutando em {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    main()
