from socket import socket, AF_INET, SOCK_DGRAM
from argparse import ArgumentParser
from select import poll, EPOLLIN

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

    
    client_address = None
    server_address = (ARGS.server_ip, int(ARGS.server_port))
    middle_address_client = (ARGS.middle_ip, int(ARGS.middle_port_1))
    middle_address_server = (ARGS.middle_ip, int(ARGS.middle_port_2))

    poller = poll()
    client_fd = client_socket.fileno()
    server_fd = server_socket.fileno()

    client_datagrams_received = 0

    client_socket.bind(middle_address_client)
    server_socket.bind(middle_address_server)
    poller.register(client_fd)
    poller.register(server_fd)

    try:
        while True:
            events = poll.poll(5)
            for event, fd in events:
                if event == EPOLLIN:
                    if fd == client_fd:
                        client_datagrams_received += 1
                        datagram, client_address = client_socket.recvfrom(4096)
                        server_socket.sendto(datagram, server_address)
                    if fd == server_fd:
                        datagram, address = server_socket.recvfrom(4096)
                        client_socket.sendto(datagram, client_address)
    except KeyboardInterrupt:
        server_socket.close()
        client_socket.close()
