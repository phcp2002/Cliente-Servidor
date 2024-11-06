import socket
import time

# Configurações do cliente
HOST = '127.0.0.1'
PORT = 5000

# Função para criar uma mensagem
def criar_mensagem(tipo, conteudo):
    return f"{tipo}:{conteudo}"

# Função para enviar uma mensagem única
def enviar_mensagem_unica(client):
    conteudo = input("Digite a mensagem para enviar: ")
    mensagem = criar_mensagem("DADOS", conteudo)
    client.sendall(mensagem.encode())
    
    # Recebe e exibe a resposta do servidor
    data = client.recv(1024)
    print(f"Resposta do servidor: {data.decode()}")

# Função para enviar uma rajada de mensagens
def enviar_rajada_de_mensagens(client):
    quantidade = int(input("Quantas mensagens deseja enviar em rajada? "))
    intervalo = float(input("Intervalo entre mensagens (em segundos): "))

    for i in range(quantidade):
        conteudo = f"Mensagem {i + 1} da rajada"
        mensagem = criar_mensagem("DADOS", conteudo)
        client.sendall(mensagem.encode())
        
        # Recebe e exibe a resposta do servidor
        data = client.recv(1024)
        print(f"Resposta do servidor para '{conteudo}': {data.decode()}")

        # Aguarda o intervalo antes de enviar a próxima mensagem
        time.sleep(intervalo)

# Função principal do cliente
def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    print(f"Conectado ao servidor {HOST}:{PORT}")

    while True:
        print("\nMenu:")
        print("1. Enviar uma única mensagem")
        print("2. Enviar uma rajada de mensagens")
        print("3. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            enviar_mensagem_unica(client)
        elif opcao == '2':
            enviar_rajada_de_mensagens(client)
        elif opcao == '3':
            mensagem = criar_mensagem("SAIR", "")
            client.sendall(mensagem.encode())
            break
        else:
            print("Opção inválida. Tente novamente.")

    client.close()
    print("Conexão encerrada.")

if __name__ == "__main__":
    main()
