--- Aplicação Cliente-Servidor para Transporte Confiável de Dados ---

Disciplina: Infra. De Comunicação
Professor: Petronio Junior

Alunos:
- Paulo Portella (phcp@cesar.school)
- Gustavo Carneiro (gcic@cesar.school)

Esta aplicação implementa um protocolo de transporte confiável na camada de aplicação, simulando características como controle de fluxo, controle de congestionamento, detecção de erros e retransmissão.
Ela permite a simulação de perdas de pacotes e erros de integridade, suportando os protocolos Go-Back-N (GBN) e Selective Repeat (SR).

--- Descrição ---

A aplicação cliente-servidor utiliza sockets UDP para comunicação e implementa um protocolo confiável na camada de aplicação.

Entre as funcionalidades estão:

Controle de fluxo: O cliente considera a janela de recepção do servidor, que pode ser atualizada dinamicamente.
Controle de congestionamento: A janela de congestionamento é ajustada com base em ACKs e NACKs.
Detecção de erros: Uso de checksum para verificar a integridade dos pacotes.
Retransmissão de pacotes: Pacotes perdidos ou com erro são retransmitidos.
Protocolos suportados: Go-Back-N (GBN) e Selective Repeat (SR).

--- Requisitos ---

Python 3.6 ou superior.
Sistemas operacionais: Windows, Linux ou macOS.

--- Execução ---

-Servidor 
Digite no terminal:
  python servidor.py

Interaja com o servidor através do menu exibido no terminal.

-Cliente
Digite em outro terminal:

  python cliente.py

Interaja com o cliente utilizando o menu exibido.


--- Comandos Disponíveis ---

- Servidor

1. Ativar/Desativar erro de integridade em ACKs
Simula erros nos ACKs enviados ao cliente.

2. Configurar pacotes para simular perdas
Especifica quais pacotes devem ser "perdidos" (não serão respondidos).

3. Alterar protocolo (Selective Repeat / Go-Back-N)
Define o protocolo a ser utilizado.

4. Alterar tamanho da janela de recepção
Atualiza dinamicamente o tamanho da janela de recepção do servidor.

5. Ver janela de recepção
Exibe o tamanho atual da janela de recepção.

6. Sair
Encerra o servidor.


- Cliente
  
1. Enviar uma única mensagem
Envia uma mensagem ao servidor.

2. Enviar várias mensagens em sequência
Envia múltiplas mensagens consecutivamente.

3. Enviar pacote com erro de checksum
Envia um pacote com erro de integridade para simulação.

4. Configurar protocolo (Selective Repeat / Go-Back-N)
Define o protocolo a ser utilizado pelo cliente.

5. Exibir status da janela de congestionamento
Mostra o tamanho atual da janela de congestionamento e da janela de recepção do servidor.

6. Sair
Encerra o cliente.


--- Testando Funcionalidades ---

- Configurar o protocolo:
No cliente, escolha a opção 4 para configurar o protocolo desejado (GBN ou SR).

- Enviar mensagens:
Utilize as opções 1 ou 2 no cliente para enviar mensagens ao servidor.

- Simular erros de integridade:
No cliente, use a opção 3 para enviar pacotes com erro de checksum.
No servidor, use a opção 1 para simular erros nos ACKs.

- Simular perdas de pacotes:
No servidor, utilize a opção 2 para configurar quais pacotes serão perdidos.

- Atualizar janela de recepção dinamicamente:
No servidor, escolha a opção 4 para alterar o tamanho da janela de recepção.
O cliente ajustará seu envio de pacotes de acordo com o novo tamanho informado nos ACKs.

- Verificar status das janelas:
No cliente, use a opção 5 para visualizar os tamanhos atuais das janelas de congestionamento e de recepção.


--- Detalhes do Protocolo ---

Formato do Pacote:

Cabeçalho:
Número de sequência (seq_num)
Número de reconhecimento (ack_num)
Tamanho da janela (window_size)
Flags (flags)
Checksum (checksum)
Dados: Conteúdo da mensagem.
Flags:

FLAG_DATA (0b0001): Pacote de dados.
FLAG_ACK (0b0010): Acknowledgement (confirmação).
FLAG_NACK (0b0100): Negative Acknowledgement (confirmação negativa).
FLAG_CONFIG (0b1000): Configuração de protocolo.
Controle de Fluxo:

O cliente respeita o menor valor entre sua janela de congestionamento e a janela de recepção do servidor, atualizada dinamicamente via ACKs.
Controle de Congestionamento:

A janela de congestionamento do cliente aumenta com ACKs positivos e diminui com NACKs ou timeouts.
Detecção e Correção de Erros:

Utiliza checksum simples para verificar integridade.
Pacotes corrompidos são descartados, e o remetente retransmite após timeout.










