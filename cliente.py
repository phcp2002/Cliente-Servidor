import socket
import threading
import struct

# Configurações gerais
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000
MAX_WINDOW_SIZE = 3
TIMEOUT = 2

# Flags
FLAG_DATA = 0b0001
FLAG_ACK = 0b0010
FLAG_NACK = 0b0100
FLAG_CONFIG = 0b1000

def calculate_checksum(data):
    checksum = 0
    for byte in data:
        checksum ^= byte
    return checksum

def create_packet(seq_num, ack_num, window_size, flags, data):
    header = struct.pack('!HHHB', seq_num, ack_num, window_size, flags)
    checksum = calculate_checksum(header + data)
    return header + struct.pack('!B', checksum) + data

def parse_packet(packet):
    header = packet[:7]
    seq_num, ack_num, window_size, flags = struct.unpack('!HHHB', header)
    checksum = packet[7]
    data = packet[8:]
    calc_checksum = calculate_checksum(header + data)
    if checksum != calc_checksum:
        return None
    return {'seq_num': seq_num, 'ack_num': ack_num, 'window_size': window_size, 'flags': flags, 'data': data}

class Client:
    def __init__(self, host, port):
        self.server_address = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.base = 0
        self.next_seq_num = 0
        self.window_size = MAX_WINDOW_SIZE
        self.congestion_window = 1
        self.timers = {}
        self.buffer = {}
        self.protocol = 'sr'

    def send_packet(self, data, simulate_error=False):
        if self.next_seq_num < self.base + self.window_size:
            seq_num = self.next_seq_num
            flags = FLAG_DATA
            packet = create_packet(seq_num, 0, self.window_size, flags, data)
            if simulate_error:
                packet = bytearray(packet)
                packet[-1] ^= 0xFF
                packet = bytes(packet)
            self.socket.sendto(packet, self.server_address)
            print(f"[CLIENT] Enviando pacote {seq_num}: {data.decode()}")
            self.buffer[seq_num] = packet
            self.next_seq_num += 1
        else:
            print("[CLIENT] Janela cheia. Aguardando...")

    def send_config(self):
        flags = FLAG_CONFIG
        data = self.protocol.encode()
        packet = create_packet(0, 0, self.window_size, flags, data)
        self.socket.sendto(packet, self.server_address)

    def resend_packet(self, seq_num):
        packet = self.buffer.get(seq_num)
        if packet:
            print(f"[CLIENT] Reenviando pacote {seq_num}")
            self.socket.sendto(packet, self.server_address)

    def receive_ack(self):
        while True:
            try:
                packet, _ = self.socket.recvfrom(1024)
                parsed = parse_packet(packet)
                if parsed:
                    if parsed['flags'] & FLAG_ACK:
                        ack_num = parsed['ack_num']
                        print(f"[CLIENT] ACK recebido: {ack_num}")
                        if ack_num >= self.base:
                            self.base = ack_num + 1
                            self.congestion_window += 1
                            print(f"[CLIENT] Janela de congestionamento aumentada para: {self.congestion_window}")
                    elif parsed['flags'] & FLAG_NACK:
                        nack_num = parsed['ack_num']
                        print(f"[CLIENT] NACK recebido: {nack_num}")
                        self.congestion_window = max(1, self.congestion_window // 2)
                        self.resend_packet(nack_num)
                else:
                    print("[CLIENT] Erro de checksum no ACK recebido. Retransmitindo último pacote.")
                    self.resend_packet(self.base)
            except OSError as e:
                print(f"[CLIENT] Erro ao receber pacote: {e}")
                break

    def check_integrity(self):
        print("\n--- VERIFICAÇÃO DE INTEGRIDADE ---")
        data = input("Digite a mensagem a ser enviada para verificação de integridade: ").encode()
        seq_num = self.next_seq_num
        flags = FLAG_DATA
        packet = create_packet(seq_num, 0, self.window_size, flags, data)
        print(f"[CLIENT] Pacote criado com checksum: {packet[-1]}")
        calc_checksum = calculate_checksum(packet[:-1])
        print(f"[CLIENT] Checksum calculado: {calc_checksum}, Checksum no pacote: {packet[-1]}")
        if calc_checksum == packet[-1]:
            print("[CLIENT] A integridade do pacote está correta.")
        else:
            print("[CLIENT] A integridade do pacote está corrompida.")

    def menu(self):
        while True:
            print("\n--- MENU DO CLIENTE ---")
            print("1. Enviar uma única mensagem")
            print("2. Enviar várias mensagens em sequência")
            print("3. Enviar pacote com erro de checksum")
            print("4. Configurar protocolo (Selective Repeat / Go-Back-N)")
            print("5. Exibir status da janela de congestionamento")
            print("6. Alterar o tamanho da janela de recepção")
            print("7. Verificar integridade do pacote")
            print("8. Sair")
            choice = input("Escolha uma opção: ").strip()
            if choice == '1':
                data = input("Digite a mensagem a ser enviada: ").encode()
                self.send_packet(data)
            elif choice == '2':
                num_messages = int(input("Número de mensagens a enviar: "))
                for _ in range(num_messages):
                    message = input("Digite a mensagem: ").encode()
                    self.send_packet(message)
            elif choice == '3':
                data = input("Digite a mensagem com erro: ").encode()
                self.send_packet(data, simulate_error=True)
            elif choice == '4':
                protocol = input("Escolha o protocolo (gbn/sr): ").strip().lower()
                if protocol in ['gbn', 'sr']:
                    self.protocol = protocol
                    self.send_config()
                else:
                    print("[CLIENT] Protocolo inválido.")
            elif choice == '5':
                print(f"Janela de congestionamento atual: {self.congestion_window}")
            elif choice == '6':
                new_window_size = int(input("Digite o novo tamanho da janela de recepção: ").strip())
                if new_window_size > 0:
                    self.window_size = new_window_size
                    print(f"Janela de recepção alterada para: {self.window_size}")
                else:
                    print("O tamanho da janela deve ser maior que zero.")
            elif choice == '7':
                self.check_integrity()
            elif choice == '8':
                print("[CLIENT] Encerrando cliente.")
                break
            else:
                print("Opção inválida.")

    def run(self):
        threading.Thread(target=self.receive_ack, daemon=True).start()
        print("[CLIENT] Cliente em execução. Use o menu para interagir.")
        self.menu()

if __name__ == "__main__":
    client = Client(SERVER_HOST, SERVER_PORT)
    client.run()
