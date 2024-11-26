import socket
import threading
import struct

# Configurações gerais
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000

# Protocolo
MAX_WINDOW_SIZE = 8
TIMEOUT = 2  # Em segundos

# Flags
FLAG_DATA = 0b0001
FLAG_ACK = 0b0010
FLAG_NACK = 0b0100
FLAG_CONFIG = 0b1000

def calculate_checksum(data):  # Calcula o checksum XOR para verificar integridade.
    checksum = 0
    for byte in data:
        checksum ^= byte
    return checksum

def create_packet(seq_num, ack_num, window_size, flags, data):  # Cria um pacote com cabeçalho, checksum e dados.
    header = struct.pack('!HHHB', seq_num, ack_num, window_size, flags)
    checksum = calculate_checksum(header + data)
    return header + struct.pack('!B', checksum) + data

def parse_packet(packet):  # Analisa um pacote recebido e verifica seu checksum.
    header = packet[:7]
    seq_num, ack_num, window_size, flags = struct.unpack('!HHHB', header)
    checksum = packet[7]
    data = packet[8:]
    calc_checksum = calculate_checksum(header + data)
    if checksum != calc_checksum:
        return None
    return {'seq_num': seq_num, 'ack_num': ack_num, 'window_size': window_size, 'flags': flags, 'data': data}

class Server:
    def __init__(self, host, port):
        self.server_address = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)
        self.expected_seq_num = 0
        self.window_size = MAX_WINDOW_SIZE
        self.congestion_window = 1  # Janela de congestionamento
        self.protocol = 'sr'  # Protocolo padrão é SR
        self.simulate_ack_error = False
        self.simulate_packet_loss = set()  # Conjunto de pacotes a serem simulados como perdidos.

    def send_ack(self, client_address, ack_num, negative=False):
        flags = FLAG_ACK if not negative else FLAG_NACK
        packet = create_packet(0, ack_num, self.window_size, flags, b'')
        if self.simulate_ack_error:
            # Simula erro no ACK
            packet = bytearray(packet)
            packet[-1] ^= 0xFF  # Modifica o checksum
            packet = bytes(packet)
            print(f"[SERVIDOR] [Erro Simulado] Enviando ACK corrompido para o pacote {ack_num}")
        else:
            print(f"[SERVIDOR] Enviando {'NACK' if negative else 'ACK'} para o pacote {ack_num}")
        self.socket.sendto(packet, client_address)

    def handle_packet(self, packet, client_address):
        parsed = parse_packet(packet)
        if not parsed:
            print("[SERVIDOR] Erro de checksum no pacote recebido. Enviando NACK.")
            self.congestion_window += 1  # Aumenta a janela quando há erro.
            print(f"[SERVIDOR] Janela de congestionamento aumentada para: {self.congestion_window}")
            self.send_ack(client_address, self.expected_seq_num, negative=True)
            return

        seq_num = parsed['seq_num']
        flags = parsed['flags']
        data = parsed['data']

        if flags & FLAG_CONFIG:  # Se o pacote for de configuração, altera o protocolo
            self.protocol = data.decode()
            print(f"[SERVIDOR] Protocolo configurado para: {self.protocol}")
            self.send_ack(client_address, 0)

        elif flags & FLAG_DATA:  # Processa pacotes de dados
            if seq_num in self.simulate_packet_loss:
                print(f"[SERVIDOR] [Simulação de Perda] Ignorando o pacote {seq_num}.")
                self.congestion_window += 1  # Aumenta a janela para pacotes perdidos
                print(f"[SERVIDOR] Janela de congestionamento aumentada para: {self.congestion_window}")
                return

            if self.protocol == 'sr':  # Selective Repeat
                if seq_num == self.expected_seq_num:
                    print(f"[SR] Processando pacote {seq_num}: {data.decode()}")
                    self.expected_seq_num += 1
                    self.send_ack(client_address, seq_num)
                elif seq_num > self.expected_seq_num:
                    print(f"[SR] Pacote fora de ordem: {seq_num}. Enviando NACK.")
                    self.send_ack(client_address, seq_num, negative=True)
                else:
                    print(f"[SR] ACK duplicado para o pacote {seq_num}")
                    self.send_ack(client_address, seq_num)

            elif self.protocol == 'gbn':  # Go-Back-N
                if seq_num == self.expected_seq_num:
                    print(f"[GBN] Processando pacote {seq_num}: {data.decode()}")
                    self.expected_seq_num += 1
                    self.send_ack(client_address, seq_num)
                else:
                    print(f"[GBN] Pacote fora de ordem. Enviando ACK do último confirmado: {self.expected_seq_num - 1}")
                    self.send_ack(client_address, self.expected_seq_num - 1)

        else:
            print("[SERVIDOR] Pacote recebido com flag desconhecida.")

    def toggle_ack_error(self):
        self.simulate_ack_error = not self.simulate_ack_error
        status = "ativado" if self.simulate_ack_error else "desativado"
        print(f"[SERVIDOR] Simulação de erro em ACK {status}.")

    def configure_packet_loss(self):
        print("Digite os números de sequência dos pacotes a serem ignorados (separados por espaço):")
        try:
            loss_input = input("Simular perda para pacotes: ")
            self.simulate_packet_loss = set(map(int, loss_input.split()))
            print(f"[SERVIDOR] Pacotes configurados para perda: {self.simulate_packet_loss}")
        except ValueError:
            print("[SERVIDOR] Entrada inválida. Nenhum pacote será perdido.")

    def display_congestion_window(self):
        print(f"[SERVIDOR] Janela de congestionamento atual: {self.congestion_window}")

    def menu(self):
        while True:
            print("\n--- MENU DO SERVIDOR ---")
            print("1. Ativar/Desativar erro de integridade em ACKs")
            print("2. Configurar pacotes para simular perdas")
            print("3. Exibir status da janela de congestionamento")
            print("4. Alterar protocolo (Selective Repeat / Go-Back-N)")
            print("5. Sair")
            choice = input("Escolha uma opção: ").strip()
            if choice == '1':
                self.toggle_ack_error()
            elif choice == '2':
                self.configure_packet_loss()
            elif choice == '3':
                self.display_congestion_window()
            elif choice == '4':
                protocol = input("Escolha o protocolo (sr/gbn): ").strip().lower()
                if protocol in ['sr', 'gbn']:
                    self.protocol = protocol
                    print(f"[SERVIDOR] Protocolo alterado para: {protocol.upper()}")
                else:
                    print("[SERVIDOR] Protocolo inválido.")
            elif choice == '5':
                print("[SERVIDOR] Encerrando o servidor.")
                break
            else:
                print("[SERVIDOR] Opção inválida.")

    def run(self):
        print("[SERVIDOR] Inicializando...")
        threading.Thread(target=self.menu, daemon=True).start()
        print("[SERVIDOR] Aguardando pacotes...")
        while True:
            try:
                packet, client_address = self.socket.recvfrom(1024)
                print(f"[SERVIDOR] Pacote recebido de {client_address}")
                self.handle_packet(packet, client_address)
            except Exception as e:
                print(f"[SERVIDOR] Erro ao receber pacote: {e}")
                break

if __name__ == "__main__":
    server = Server(SERVER_HOST, SERVER_PORT)
    server.run()

