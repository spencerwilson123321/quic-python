from QUIC import *

"""
    Test Case #1:
        1. Accept a client connection.
        2. Close the client connection.
"""

if __name__ == "__main__":

    server = QUICSocket(local_ip="10.0.0.131")
    server.listen(8000)
    client = server.accept() # Accept a connection.
    address = None
    # Get the 5 client datagrams.
    sock = client._socket
    datagrams_received = 0
    while datagrams_received < 4:
        try:
            datagram = None
            datagram, address = sock.recvfrom(1024)
            print(datagram)
            if datagram:
                datagrams_received += 1
        except BlockingIOError:
            pass

    # Send an AckFrame which will cause a packet loss detection
    # and retransmission.
    frame = AckFrame(largest_acknowledged = 6, ack_delay=0, ack_range_count=1, first_ack_range=3, ack_range=[AckRange(gap=1, ack_range_length=2)])
    hdr = ShortHeader(destination_connection_id=0, packet_number=2)
    pkt = Packet(header=hdr, frames=[frame])

    sock.sendto(pkt.raw(), address)
    # msg = b""
    # while not msg:
    #     msg, disconnected = client.recv(1, 1024)
    # print(f"Received: {msg}")

    # client.send(1, msg)
    # print(f"Sent: {msg}")

    # msg = b""
    # while not msg:
    #     msg, disconnected = client.recv(1, 1024)
    # print(f"Received: {msg}")

    # client.send(1, msg)
    # print(f"Sent: {msg}")

    client.release()
