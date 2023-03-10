from socket import socket, AF_INET, SOCK_DGRAM
from argparse import ArgumentParser
from select import poll, POLLIN

PARSER = ArgumentParser()
PARSER.add_argument("middle_ip", help="The IPv4 address of this machine.")
PARSER.add_argument("middle_port_1", help="The port this machine will listen on.")
PARSER.add_argument("middle_port_2", help="The port this machine will listen on.")
PARSER.add_argument("server_ip", help="The server IPv4 address to forward packets to.")
PARSER.add_argument("server_port", help="The server port to forward packets to.")

ARGS = PARSER.parse_args()

if __name__ == "__main__":
    client_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.setblocking(0)
    server_socket.setblocking(0)
    
    client_address = None
    server_address = (ARGS.server_ip, int(ARGS.server_port))
    middle_address_client = (ARGS.middle_ip, int(ARGS.middle_port_1))
    middle_address_server = (ARGS.middle_ip, int(ARGS.middle_port_2))
    client_socket.bind(middle_address_client)
    server_socket.bind(middle_address_server)

    poller = poll()
    client_datagrams_received = 0

    poller.register(server_socket)
    poller.register(client_socket)

    try:
        while True:
            events = poller.poll()
            for fd, event in events:
                if event & POLLIN:
                    if fd == server_socket.fileno():
                        print("SERVER --> CLIENT")
                        datagram, address = server_socket.recvfrom(4096)
                        client_socket.sendto(datagram, client_address)
                    if fd == client_socket.fileno():
                        print("CLIENT --> SERVER")
                        client_datagrams_received += 1
                        datagram, client_address = client_socket.recvfrom(4096)
                        server_socket.sendto(datagram, server_address)
    except KeyboardInterrupt:
        server_socket.close()
        client_socket.close()
