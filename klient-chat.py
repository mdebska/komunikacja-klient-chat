import socket
import threading

nickname = input("Choose your nickname: ")

# Laczenie z serwerem
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 1234))


def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            # zapytanie serwera o nick + wyslanie nicku
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            # zwykla wiadomosc
            else:
                print(message)
        # zamknicie serwera
        except:
            print("An error occurred!")
            client.close()
            break


# pisanie i wyslanie wiadomosci do serwera
def write():
    while True:
        message = f'{input("")}'
        client.send(message.encode('ascii'))


# wywolywanie funkcji
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()