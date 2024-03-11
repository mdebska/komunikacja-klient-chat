import socketserver

host = 'localhost'
port = 1234

clients = {}  # słownik pomocnicza
nicknames = {}  # słownik nicków wszystkich użytkowników, którzy są ONLINE
unsend = []  # tablica przechowywująca nadawce, odbiorce, wiadomość


def unicast(client, message):
    client.send(message)


def broadcast(message):
    for client in clients.values():
        client.send(message)


class ChatHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.send('NICK'.encode('ascii'))  # odbieranie nicku użytkownika od klienta
        nickname = self.request.recv(1024).decode('ascii')  # nazwa uzytkownika
        nicknames[self.request] = nickname
        clients[nickname] = self.request

        print(f"{nickname} join the server!")
        unicast(self.request, f"Connected to the server!\n".encode('ascii'))

        while True:
            try:
                # sprawdzanie czy w unsend jest jakas wiadomosc do danego klienta
                if len(unsend) > 0:
                    for i in range(len(unsend)):
                        if unsend[i][1] == nickname:
                            unicast(self.request, f'New private message from {unsend[i][0]}: {unsend[i][2]}'.encode('ascii'))
                            del unsend[i]

                # Odczytywanie wiadomosci
                message = self.request.recv(1024)
                message = message.decode('ascii')
                error_sent = False

                # Przesyłanie wiadomości do danego klienta
                if message.startswith('@'):
                    receiver, content = message[1:].split(':', 1)
                    # gdy dany odbiorca jest ONLINE
                    if receiver in clients:
                        recipient = clients[receiver]
                        unicast(recipient, f"Private message from {nicknames[self.request]}:{content}\n".encode('ascii'))

                    # gdy dany odbiorca jest OFLINE - wrzucanie wiadomosci do unsend
                    else:
                        if not error_sent:
                            unicast(self.request, f"Receiver '{receiver}' not available!\n The message will be sent if {receiver} comes online.\n".encode('ascii'))
                            unsend.append((nickname, receiver, content))
                # Gdy wiadomosc nie jest sprecyzowana do danego klienta - wysylanie do wszystkich
                else:
                    broadcast(f"{nicknames[self.request]}: {message}\n".encode('ascii'))
            # wyjątek - klient wychodzi z serwera
            except:
                nickname = nicknames[self.request]
                del clients[nickname]
                del nicknames[self.request]
                self.request.close()
                broadcast(f'{nickname} left the chat!\n'.encode('ascii'))
                break


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


# ThreadingMixIn - pozwala na połączenie wielu klientów
# TCPServer - tworzy serwer i nasłuchuje połączenia nowych klientów


server = ThreadedTCPServer((host, port), ChatHandler)
print("Server started on port", port)
server.serve_forever()
