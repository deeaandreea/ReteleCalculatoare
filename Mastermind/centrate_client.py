import socket
import time
from threading import Thread

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 1234 # server's port
SEPARATOR = "<SEP>" # we will use this to separate the client name & message

# initialize TCP socket
client_socket = socket.socket()

def introdu_incercare():
    while True:
        guess = input('Ghiceste numarul de 4 cifre diferite: ')
        if guess == 'exit':
            return 'exit'
        if len(guess) != 4 or not guess.isnumeric():
            print('Incercare invalida. Incearca din nou.')
        else:
            return guess

def listen_for_messages():
    while True:
        # citire raspuns server
        raspuns = client_socket.recv(1024).decode()
        # centrate, necentrate = map(int, raspuns.split('-'))
        if raspuns == '':
            continue
        r1, r2 = raspuns.split('-')
        if not r2.isnumeric():
            client_name = r2
            print(f'\n{client_name} a ghicit numarul.')
            print('A fost generat un nou numar de 4 cifre diferite.')
            print('Ghiceste numarul de 4 cifre diferite: ')
            continue

        centrate = int(r1)
        necentrate = int(r2)

        if centrate == 4:
            print('Felicitari! Ai ghicit numarul.')
            print('A fost generat un nou numar de 4 cifre diferite.\n')
            # break
        else:
            print('Nu ai ghicit numarul, dar ai:')
            print(f'  - {centrate} centrate (cifre care se gasesc in numar pe aceeasi pozitie): ')
            print(f'  - {necentrate} necentrate (cifre care se gasesc in numar, dar nu pe aceeasi pozitie)')


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    print(f"[*] Conectare la server {SERVER_HOST}:{SERVER_PORT}...")
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print("[+] Conectat")

    # cere introducerea numelui clientului
    nume_client = input("Nume client: ")

    # make a thread that listens for messages to this client & print them
    thread = Thread(target=listen_for_messages)
    # make the thread daemon so it ends whenever the main thread ends
    thread.daemon = True
    # start the thread
    thread.start()

    while True:
        time.sleep(1)
        incercare = introdu_incercare()
        if incercare == 'exit':
            break
        de_trimis = f'{nume_client}{SEPARATOR}{incercare}'
        client_socket.send(de_trimis.encode())


