import random
import socket
import select

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 1234
BACKLOG = 5  # Numarul de conexiuni posibile
SEPARATOR = '<SEP>'

def generare_numar():
    cifre = list(range(10))  # Creează o listă cu cifrele de la 0 la 9
    random.shuffle(cifre)    # Amestecă cifrele în ordine aleatoare
    if cifre[0] == 0:        # Verifică dacă prima cifră este zero
        cifre[0], cifre[1] = cifre[1], cifre[0]  # Schimbă prima cifră cu a doua
    numar = cifre[:4]        # Ia primele patru cifre din lista amestecată
    return int(''.join(map(str, numar)))  # Converteste lista de cifre in numar intreg

def evaluare_incercare(code, guess):
    cod = str(code)
    incercare = str(guess)
    ghicite = 0
    suntinnum = 0
    # lista centrate[] pastreaza cifrele care sunt corecte
    centrate = []
    necentrate = []

    for i in range(0, 4):
        # verificam egalitatea cifrelor
        if (incercare[i] == cod[i]):
            # incrementam numarul de cifre ghicite corect
            ghicite += 1
            # si salvam cifra in lista centrate[].
            centrate.append(incercare[i])
        else:
            for j in range(0, 4):
                if (j != i) and (incercare[i] == cod[j]):
                    suntinnum += 1
                    necentrate.append(incercare[i])
            continue
    return ghicite, suntinnum


# trimite mesajul celorlalti clientilor conectati
def broadcast_message(sockets, socket, message):
    for sock in sockets:
        try:
            if (sock != socket):
                sock.send(message.encode())
        except socket.error as e:
            print('Socket error:', str(e))
            sock.close()


code = generare_numar()
print('Numarul de 4 cifre diferite generat:', code)

client_sockets = []
inputs = []

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(BACKLOG)
    print(f'[*] Server pornit {SERVER_HOST}:{SERVER_PORT}. Asteapta clienti sa se conecteze...')

    inputs.append(server_socket)

    while True:
        readable, _, _ = select.select(inputs, [], [])

        for sock in readable:
            # a fost primita o cerere noua de conexiune de la un client
            if sock is server_socket:
                client_socket, client_address = server_socket.accept()
                print('Client nou conectat:', client_address)
                client_sockets.append(client_socket)
                inputs.append(client_socket)
            # mesaj primit de la un client
            else:
                try:
                    data = sock.recv(1024).decode()
                    if data:
                        msg = data.strip()
                        # print(msg)
                        idx = msg.find(SEPARATOR)
                        client_name = msg[:idx]
                        incercare = str(msg[idx + len(SEPARATOR):])
                        incercare = incercare.strip()
                        print(f'Incercare primita de la {client_name}: {incercare}')

                        centrate, necentrate = evaluare_incercare(code, incercare)

                        response = f'{centrate}-{necentrate}'
                        sock.send(response.encode())

                        if centrate == 4:
                            print(f'{client_name} a ghicit numarul. Joc incheiat.')
                            # trimite mesajul catre toate connected sockets
                            mesaj_final = f'4-{client_name}'
                            broadcast_message(client_sockets, sock, mesaj_final)
                            # genereaza un alt numar
                            code = generare_numar()
                            print(f'\nNumar nou de 4 cifre diferite generat: {code}')

                    else:
                        print('Client deconectat')
                        if sock in inputs:
                            inputs.remove(sock)
                            client_sockets.remove(sock)
                            sock.close()

                except socket.error as e:
                    print('Socket error:', str(e))
                    inputs.remove(sock)
                    client_sockets.remove(sock)
                    sock.close()

        if len(client_sockets) == 0:
            print('Toti clientii au fost deconectati. Oprire server.')
            break
