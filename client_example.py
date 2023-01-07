from QUIC.QUICPacket import *


if __name__ == "__main__":

    hdr = LongHeader(type="initial")
    frames = []
    pkt = Packet(header=hdr, frames=frames)
    print(hdr)
    
    # addr = ("10.0.0.159", 8001)
    # sock = QUICSocket()
    # sock.connect(addr)
    # data, addr = sock.recv(1024)
    # print(data)
    # print(addr)
    # sock.send(b"response", 1)
    # sock.close()
