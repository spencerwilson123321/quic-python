from QUIC.QUICPacket import *
from struct import unpack

if __name__ == "__main__":

    # hdr = LongHeader(type="initial", destination_connection_id=4294967295, source_connection_id=19823712, packet_number=128397)
    # print(hdr)
    # print(hdr.raw())
    # unpacked = struct.unpack("!BBBLBLBLI", hdr.raw())
    # print(unpacked)

    # hdr = ShortHeader(destination_connection_id=4294967295, packet_number=128397)
    # print(hdr)
    # print(hdr.raw())
    # unpacked = struct.unpack("!BLL", hdr.raw())
    # print(unpacked)

    frame = StreamFrame(stream_id=1, offset=1182123, length=10, data=b"HelloWorld")
    print(frame)
    print(frame.raw())
    
