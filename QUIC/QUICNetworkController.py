from .QUICPacketParser import parse_packet_bytes, PacketParserError
from .QUICPacket import *
from .QUICConnection import ConnectionContext, create_connection_id
from .QUICEncryption import EncryptionContext
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR
import math
from time import time, sleep
import logging

# Initialize logging facility.
def setup_logger(name: str, filepath: str, level=logging.DEBUG):
    file_handler = logging.FileHandler(filepath)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    return logger

sent_log = setup_logger("sent_log", "sent.log")
received_log = setup_logger("received_log", "received.log")


# Congestion Controller States
SLOW_START = 1
RECOVERY = 2
CONGESTION_AVOIDANCE = 3

# Congestion Controller Data
INFINITY = math.inf
MAX_DATAGRAM_SIZE = 1200
SAFE_DATAGRAM_PAYLOAD_SIZE = 512 # bytes
INITIAL_CONGESTION_WINDOW = MAX_DATAGRAM_SIZE*10 # Initial window is 10 times max datagram size RFC 9002
MINIMUM_CONGESTION_WINDOW = MAX_DATAGRAM_SIZE*2  # Minimum window is 2 times max datagram size RFC 9002

# This means we have ended the connection.
DISCONNECTED = 1
# This means we have completed the handshake and are currently connected.
CONNECTED = 2

# This means we have sent an INITIAL packet and are waiting
# for a response. 
INITIALIZING = 3

# This means that we are listening for connections.
LISTENING_INITIAL = 4
LISTENING_HANDSHAKE = 5

# This means that we have closed the connection.
CLOSED = 6


# Slow Start:
# congestion window is increased by the number of acknowledged bytes every time an ACK is processed.
# upon packet loss being detected, the controller enters the recovery state.

# Recovery:
# Slow start gets set to half of the congestion window.
# When a packet sent during recovery is acked, then we exit recovery and enter congestion avoidance.

# Congestion Avoidance:
# The controller is in congestion avoidance mode when the congestion window is equal to or greater than the slow start threshold and isn't in recovery mode.
# For each full congestion window amount of bytes acknowledged, increase the congestion window by 1 maximum datagram size.
# If a packet is lost, then enter recovery.

# Ack-eliciting Frames:
# Frames other than ACK, PADDING, CONNECTION_CLOSE are ack-eliciting.

# Ack-eliciting Packets:
# Packets that contain ack-eliciting frames elicit an ACK from the receiver 
# within the maximum acknowledgement delay.

# In-flight Packets:
# Packets are considered in-flight when they are ack-eliciting and they
# have been sent but not acknowledged or declared lost.

# Congestion Control Important Information:
# --> All packets must be acknowledged.
# --> Packets with frames other than CONNECTION_CLOSE and ACK count towards bytes in flight.
# --> 

# Sender Side Congestion Control:
# Send all packets that you can while staying below the congestion control limits.
# Must track how many bytes are in flight with each packet sent.
# Must store packets in a buffer until they get acknowledged.
# When a packet is considered lost, resend the packets frames in a new packet.

# Loss Epoch
# When a packet is lost, a timer is started called "loss epoch".
# When a packet sent after the loss epoch has started is acknowledged,
# then the loss epoch ends.

# RTT Measurement:
# Track when each packet is sent.
# Track when each packet is acked.
# These values are used as an RTT sample.
# BUT we also need to follow these rules:
# - The largest acknowledged packet number must be newly acknowledged.
# - At least one of the newly acknowledged packets was ack-eliciting.

# latest_rtt = ack_time - send_time_of_largest_acked.

# Minimum RTT:
# min_rtt is tracked and represents the minimum rtt observed.
# Can be used by loss detection to reject implausibly small RTT samples.
# Each time an rtt sample is taken, we must potentially update min_rtt.



class PacketSentInfo:

    def __init__(self, in_flight=False, sent_bytes=0, time_sent=0.0, packet_number=0, ack_eliciting=False, packet=None):
        self.in_flight: bool = in_flight
        self.sent_bytes: int = sent_bytes
        self.time_sent: float = time_sent
        self.ack_eliciting: bool = ack_eliciting
        self.packet_number: int = packet_number
        self.packet: Packet = packet


class PacketReceivedInfo:

    def __init__(self, packet_number=0, ack_packet=False):
        self.packet_number: int = packet_number
        self.ack_packet: bool = ack_packet


class QUICPacketizer:
    """
        Manages transmission order of packets:
        1. Manages which packet number to use next. --> This is just an incrementing counter.
        2. Constructs data packets containing stream frames.
    """

    def __init__(self):
        self._next_packet_number = 0


    def get_next_packet_number(self):
        next = self._next_packet_number
        self._next_packet_number +=1
        return next
    

    def create_header(self, header_type: int, connection_context: ConnectionContext) -> LongHeader or ShortHeader:
        if header_type in [HT_INITIAL, HT_HANDSHAKE, HT_RETRY]:
            return LongHeader(
                    type=header_type,
                    destination_connection_id=connection_context.get_peer_connection_id(),
                    source_connection_id=connection_context.get_local_connection_id(),
                    packet_number=self.get_next_packet_number()
                )
        if header_type in [HT_DATA]:
            return ShortHeader(
                destination_connection_id=connection_context.get_peer_connection_id(),
                packet_number=self.get_next_packet_number()
            )
        return None
        

    def packetize_initial_packet(self, connection_context: ConnectionContext) -> Packet:
        hdr = self.create_header(HT_INITIAL, connection_context)
        frames = [] # TODO Add crypto frames.
        return Packet(header=hdr, frames=frames)
    

    def packetize_connection_close_packet(self, connection_context: ConnectionContext) -> Packet:
        hdr = self.create_header(HT_DATA, connection_context)
        reason = b"Normal Connection Termination"
        frames = [ConnectionCloseFrame(error_code=1, reason_phrase_len=len(reason), reason_phrase=reason)]
        return Packet(header=hdr, frames=frames)


    def packetize_handshake_packet(self, connection_context: ConnectionContext) -> Packet:
        hdr = self.create_header(HT_HANDSHAKE, connection_context)
        frames = []
        return Packet(header=hdr, frames=frames)


    def packetize_connection_response_packets(self, connection_context: ConnectionContext) -> list[Packet]:
        hdr1 = self.create_header(HT_INITIAL, connection_context)
        hdr2 = self.create_header(HT_HANDSHAKE, connection_context)
        frames1 = []
        frames2 = []
        initial, handshake = Packet(header=hdr1, frames=frames1), Packet(header=hdr2, frames=frames2)
        return [initial, handshake]
    

    def create_ack_frame(self, packet_numbers_received: list[int]) -> AckFrame:
        # If the received packets list is length 1
        # Create a simple ack frame.
        if len(packet_numbers_received) == 1:
            return AckFrame(largest_acknowledged=packet_numbers_received[0], ack_delay=0, ack_range_count=0, ack_range=[])
        # If the received packets list is greater than 1.
        # We sort the packet number list.
        # Then we incrementally create AckRanges.
        # In the resulting AckRanges, an AckRange with gap 0 is the most recent AckRange,
        # from this AckRange we can get first ack range value.
        packet_numbers_received.sort()
        ranges = []
        count = 0
        for i in range(0, len(packet_numbers_received)):
            count += 1
            if i == len(packet_numbers_received)-1:
                ranges.append(AckRange(gap=0, ack_range_length=count))
                break
            if packet_numbers_received[i+1] != packet_numbers_received[i]+1:
                ranges.append(AckRange(gap=packet_numbers_received[i+1] - packet_numbers_received[i] - 1, ack_range_length=count))
                count = 0
        first_ack_range = ranges[-1].ack_range_length - 1
        largest_acknowledged = packet_numbers_received[-1]
        ranges.remove(ranges[-1])
        return AckFrame(largest_acknowledged=largest_acknowledged, ack_delay=0, ack_range_count=len(ranges), first_ack_range=first_ack_range, ack_range=ranges)


    def packetize_acknowledgement(self, connection_context: ConnectionContext, packet_numbers_received: list[int]) -> Packet:

        # If the received packets list is length 0
        # We cannot create an ack if we haven't received any packets.
        if not packet_numbers_received:
            return None

        hdr = self.create_header(HT_DATA, connection_context)
        frames = [self.create_ack_frame(packet_numbers_received)]
        pkt = Packet(header=hdr, frames=frames)
        return pkt


    def packetize_stream_data(self, stream_id: int, data: bytes, connection_context: ConnectionContext, send_streams: dict) -> list[Packet]:
        packets = []
        MAX_ALLOWED = SAFE_DATAGRAM_PAYLOAD_SIZE-LONG_HEADER_SIZE-STREAM_FRAME_SIZE
        # If the length of this data would go over the safe datagram size - long header size - stream frame size,
        # then we need to split this data into multiple QUIC packets.
        datasize = len(data)
        if datasize > MAX_ALLOWED:
            bytes_written = 0
            while bytes_written < datasize:
                data_chunk = data[0:MAX_ALLOWED]
                hdr = self.create_header(HT_DATA, connection_context)
                frames = [StreamFrame(stream_id=stream_id, offset=send_streams[stream_id].get_offset(), length=len(data_chunk), data=data_chunk)]
                packets.append(Packet(header=hdr, frames=frames))
                send_streams[stream_id].update_offset(len(data_chunk))
                data = data[MAX_ALLOWED:]
                bytes_written += len(data_chunk)
        else:
            hdr = self.create_header(HT_DATA, connection_context)
            frames = [StreamFrame(stream_id=stream_id, offset=send_streams[stream_id].get_offset(), length=len(data), data=data)]
            packets.append(Packet(header=hdr, frames=frames))
            send_streams[stream_id].update_offset(len(data))
        return packets




class SendStream:

    def __init__(self, stream_id: int):
        self.stream_id = stream_id
        self.offset = 0

    def get_offset(self) -> int:
        return self.offset

    def update_offset(self, data_length: int) -> None:
        self.offset += data_length




class ReceiveStream:

    def __init__(self, stream_id: int):
        self.stream_id = stream_id
        self.data = b""
        self.offset = 0
        self.buffered_frames: list[StreamFrame] = []

    def buffer(self, frame: StreamFrame):
        self.buffered_frames.append(frame)

    def write(self, new_data: bytes):
        self.offset += len(new_data)
        self.data += new_data
        self.process_buffered_frames()

    def process_buffered_frames(self):
        frames_to_remove = []
        for frame in self.buffered_frames:
            if self.offset == frame.offset:
                self.data += frame.data
                self.offset += len(frame.data)
                frames_to_remove.append(frame)
        for frame in frames_to_remove:
            self.buffered_frames.remove(frame)

    def read(self, num_bytes: int) -> bytes:
        data = self.data[0:num_bytes]
        self.data = self.data[num_bytes:]
        return data





class QUICNetworkController:
    """
        When a send_stream_data or read_stream_data function is called:
            Invoke the receiver_side_controller to read and parse QUIC packets and return them to the NetworkController for processing.
                Received data can be:
                    1. Stream Data --> This needs to be written to a stream buffer inside of the network controller object.
                    2. Acks        --> This information is needed to update the sender side controller's internal state (congestion window, etc).
                        2.1. Packet loss
            If this is a send_stream_data call:
                Once the received packets are processed, then we can send our stream data by invoking the sender side controller.
                The sender side controller will packetize the data and send it based on it's congestion window etc.
            If this is a read_stream_data call:
                We just return the requested number of bytes from the stream buffer.
    """

    def __init__(self):

        self._connection_context: ConnectionContext = ConnectionContext()
        self._encryption_context: EncryptionContext = EncryptionContext()
        self._sender_side_controller = QUICSenderSideController()
        self._packetizer = QUICPacketizer()
        self._receive_streams = dict() # Key: Stream ID (int) | Value: Stream object
        self._send_streams = dict()
        self.buffered_packets = []
        self.new_socket = None
        self.peer_issued_connection_closed = False

        # ---- Handshake Data ----
        self.handshake_complete = False
        self.server_initial_received = False
        self.server_handshake_received = False
        self.client_initial_received = False
        self.client_handshake_received = False
        self.state = DISCONNECTED
        self.last_peer_address_received = None

        # ---- Acknowledgement Data ----
        self.largest_acknowledged = -1
        self.largest_packet_number_received: int = 0
        self.packet_numbers_received: list[int] = []
    


    def initiate_connection_termination(self, udp_socket: socket) -> None:
        """
            1. Send short header packet with ConnectionClose Frame.
                1. Use the packetizer to create a ConnectionClose packet.
                2. transmit the packet using the regular functions.
                3. Close the underlying UDP socket.
                4. Update the connection context information.
        """
        connection_close_packet = self._packetizer.packetize_connection_close_packet(self._connection_context)
        self.send_packets(udp_socket=udp_socket, packets=[connection_close_packet])
        udp_socket.close()
        self._connection_context.connected = False
        self.state = CLOSED


    def respond_to_connection_termination(self, udp_socket: socket):
        udp_socket.close()
        self._connection_context.connected = False
        self.state = CLOSED


    def is_client_handshake_complete(self) -> bool:
        return self.server_handshake_received and self.server_initial_received

    def is_server_handshake_complete(self) -> bool:
        return self.client_handshake_received and self.client_initial_received

    def set_buffered_packets(self, buffered_packets: list):
        self.buffered_packets = buffered_packets
    
    def get_buffered_packets(self) -> list:
        return self.buffered_packets

    def set_packetizer(self, packetizer: QUICPacketizer):
        self._packetizer = packetizer
    
    def get_packetizer(self) -> QUICPacketizer:
        return self._packetizer

    def set_state(self, state: int) -> None:
        self.state = state


    def get_state(self) -> int:
        return self.state
    

    def set_receive_streams(self, recv_streams: dict):
        self._receive_streams = recv_streams


    def get_receive_streams(self) -> dict:
        return self._receive_streams


    def set_send_streams(self, send_streams: dict):
        self._send_streams = send_streams


    def get_send_streams(self) -> dict:
        return self._send_streams


    def set_encryption_context(self, encryption_context: EncryptionContext) -> None:
        self._encryption_context = encryption_context


    def get_encryption_context(self) -> EncryptionContext | None:
        return self._encryption_context 
    

    def set_connection_context(self, connection_context: ConnectionContext) -> None:
        self._connection_context = connection_context


    def get_connection_context(self) -> ConnectionContext | None:
        return self._connection_context 


    def create_stream(self, stream_id: int) -> None:
        self._receive_streams[stream_id] = ReceiveStream(stream_id=stream_id)
        self._send_streams[stream_id] = SendStream(stream_id=stream_id)



    def listen(self, udp_socket: socket):
        # When a socket is listening, we need to bind it to the wildcard
        # address so that it doesn't associate itself with incoming connections.
        self.state = LISTENING_INITIAL
        udp_socket.bind(("", self._connection_context.get_local_port()))



    def create_connection(self, udp_socket: socket, server_address: tuple[str, int]):
        
        if self.state != DISCONNECTED:
            print("Socket must be DISCONNECTED to create a connection.")
            exit(1)

        # ---- UPDATE 5-TUPLE ----
        udp_socket.connect(server_address)

        # ---- INITIALIZE CONNECTION CONTEXT ----
        self._connection_context.set_peer_address(server_address)
        self._connection_context.set_peer_connection_id(create_connection_id())

        # ---- PACKETIZE INITIAL PACKET ----
        initial = self._packetizer.packetize_initial_packet(self._connection_context)
        self.send_packets([initial], udp_socket)
        self.state = INITIALIZING

        # ---- PROCESSING RESPONSE ----
        while not self.is_client_handshake_complete():
            packets = self.receive_new_packets(udp_socket)
            self.process_packets(packets, udp_socket)
        
        # ---- Connection Complete ----
        self.state = CONNECTED
        self.create_stream(1)




    def accept_connection(self, udp_socket: socket) -> ConnectionContext:
        if self.state != LISTENING_INITIAL:
            print("Must be in LISTENING state to accept()")
            exit(1)
        while not self.is_server_handshake_complete():
            if self.new_socket:
                packets = self.receive_new_packets(self.new_socket)
                self.process_packets(packets, self.new_socket)
            else:
                packets = self.receive_new_packets(udp_socket)
                self.process_packets(packets, udp_socket)
        # self.client_initial_received = False
        # self.client_handshake_received = False
        self.state = CONNECTED
        return self
        # return self.new_socket, self._connection_context, self._encryption_context, self.buffered_packets, self._receive_streams, self._send_streams, self.state, self._packetizer




    def send_stream_data(self, stream_id: int, data: bytes, udp_socket: socket) -> bool:
        # Check for new packets to process and process them.
        packets_to_process = self.receive_new_packets(udp_socket)
        self.process_packets(packets_to_process, udp_socket)

        # If the connection has been closed, we return -1.
        if self.peer_issued_connection_closed:
            return False

        # Packetize the stream data.
        packets: list[Packet] = self._packetizer.packetize_stream_data(stream_id, data, self._connection_context, self._send_streams)
        # Add the currently buffered packets to the list of packets to send.

        could_not_send: list[Packet] = self.send_packets(packets, udp_socket)
        while could_not_send:
            # Reprocess packets that could not be sent.
            packets_to_process = self.receive_new_packets(udp_socket)
            self.process_packets(packets_to_process, udp_socket)
            could_not_send = self.send_packets(could_not_send, udp_socket)        
        return True




    def send_packets(self, packets: list[Packet], udp_socket: socket) -> list[Packet]:
        could_not_send: list[Packet] = []
        for packet in packets:
            sent_log.debug(f"Sent: \n{packet}")
            if self.is_ack_eliciting(packet):
                # If the packet is ack eliciting,
                # then send it with congestion control.
                if self._sender_side_controller.can_send():
                    # bytes in flight < congestion window
                    try:
                        self._sender_side_controller.send_packet_cc(packet, udp_socket, self._connection_context)
                    except ConnectionRefusedError:
                        pass
                else:
                    # bytes in flight >= congestion window
                    # Need to wait to receive more acks before continuing to send.
                    could_not_send.append(packet)
            else:
                # This is an Ack, Padding, or ConnectionClose packet,
                try:
                    self._sender_side_controller.send_non_ack_eliciting_packet(packet, udp_socket, self._connection_context)
                except ConnectionRefusedError:
                    pass
        return could_not_send




    def read_stream_data(self, stream_id: int, num_bytes: int, udp_socket: socket) -> tuple[bytes, bool]:
        """
            This function will block until at least some data has been read.
        """
        # Receive and process new packets.
        packets: list[Packet] = self.receive_new_packets(udp_socket)
        self.process_packets(packets, udp_socket)
        # Now we can read from the receive_stream.
        data: bytes = self._receive_streams[stream_id].read(num_bytes)
        return data, self.peer_issued_connection_closed




    def is_active_stream(self, stream_id: int) -> bool:
        return stream_id in self._receive_streams




    def is_ack_eliciting(self, packet: Packet) -> bool:
        for frame in packet.frames:
            if frame.type not in [FT_ACK, FT_PADDING, FT_CONNECTIONCLOSE]:
                return True
        return False




    def create_and_send_acknowledgements(self, udp_socket: socket) -> None:
        ack_pkt: Packet = self._packetizer.packetize_acknowledgement(self._connection_context, self.packet_numbers_received)
        self.send_packets([ack_pkt], udp_socket)




    def update_largest_packet_number_received(self, packet: Packet) -> None:
        self.largest_packet_number_received = max(packet.header.packet_number, self.largest_packet_number_received)




    def update_received_packet_numbers(self, pkt_num: int) -> None:
        if pkt_num not in self.packet_numbers_received:
            self.packet_numbers_received.append(pkt_num)




    def process_short_header_packet(self, packet: Packet) -> None:
        # Processing Short Header Packet Frames:
        # 1. Stream Frame --> Write to stream or buffer data.
        # 2. Ack Frame    --> Remove from packets_sent, decrement bytes_in_flight, other congestion control stuff.
        for frame in packet.frames:
            if frame.type == FT_STREAM:
                self.on_stream_frame_received(frame)
            # if frame.type == FT_ACK:
            #     self.on_ack_frame_received(frame)
            if frame.type == FT_CONNECTIONCLOSE:
                self.peer_issued_connection_closed = True
            # TODO: Add checks for other frame types i.e. StreamClose, ConnectionClose, etc.




    def process_long_header_packet(self, packet: Packet, udp_socket: socket) -> None:

        # Client has sent the HT_INITIAL packet to the server.
        # Client is waiting for the HT_INITIAL and HT_HANDSHAKE response.
        if self.get_state() == INITIALIZING:
            if packet.header.type == HT_INITIAL:
                self._connection_context.set_peer_address(self.last_peer_address_received)
                self._connection_context.set_local_connection_id(packet.header.destination_connection_id)
                self.server_initial_received = True
            if packet.header.type == HT_HANDSHAKE:
                self.server_handshake_received = True
                if self.server_initial_received:
                    packet = self._packetizer.packetize_handshake_packet(self._connection_context)
                    self.send_packets([packet], udp_socket)
                    self.state = CONNECTED
                else:
                    self.buffered_packets.append(packet)
                    self.state = INITIALIZING
            return
        
        # Server is listening for INITIAL packets from clients.
        if self.get_state() == LISTENING_INITIAL:
            # When we are listening for INITIAL packets,
            # we only care about INITIAL packets so buffer all other types.
            if packet.header.type == HT_INITIAL:
                self._connection_context.set_peer_address(self.last_peer_address_received)
                self._connection_context.set_local_connection_id(packet.header.destination_connection_id)
                self._connection_context.set_peer_connection_id(create_connection_id())
                self.new_socket = socket(AF_INET, SOCK_DGRAM)
                self.new_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                self.new_socket.bind(self._connection_context.get_local_address())
                self.new_socket.connect(self._connection_context.get_peer_address())
                packets = self._packetizer.packetize_connection_response_packets(self._connection_context)
                self.send_packets(packets, self.new_socket)
                self.client_initial_received = True
                self.state = LISTENING_HANDSHAKE
                return
            self.buffered_packets.append(packet)
            return

        # Server has received the INITIAL packet from the client and has sent a response.
        # When we receive a client handshake, it finalizes the handshake procedure.
        # We must buffer all other packets at this point.
        if self.get_state() == LISTENING_HANDSHAKE:
            if packet.header.type == HT_HANDSHAKE:
                self.client_handshake_received = True
                return
            self.buffered_packets.append(packet)
            return




    def process_packets(self, packets: list[Packet], udp_socket: socket) -> None:

        if not packets:
            return

        # We should process long header packets first.
        lh_packets = [packet for packet in packets if packet.header.type in [HT_INITIAL, HT_HANDSHAKE, HT_RETRY]]
        sh_packets = [packet for packet in packets if packet.header.type in [HT_DATA]]

        for packet in lh_packets:
            self.process_long_header_packet(packet, udp_socket)
        if self.state != CONNECTED:
            self.buffered_packets += sh_packets
        else:
            for packet in sh_packets:
                self.process_short_header_packet(packet)
        # ---- PROCESS HEADER INFORMATION ----
        # 1. Update the largest packet number seen so far.
        # 2. Store which packet numbers have been received.
        # 3. Send acknowledgement if the packet is ack-eliciting.
        if packet.header.type == HT_DATA and self.state in [LISTENING_HANDSHAKE, LISTENING_INITIAL]:
            return

        for packet in packets:
            self.update_largest_packet_number_received(packet)
            self.update_received_packet_numbers(packet.header.packet_number)
            if self.is_ack_eliciting(packet):
                pkt = self._packetizer.packetize_acknowledgement(self._connection_context, self.packet_numbers_received)
                self.send_packets([pkt], udp_socket)



    def receive_new_packets(self, udp_socket: socket, block=False):
        packets: list[Packet] = [] + self.buffered_packets
        self.buffered_packets = []
        datagrams: list[bytes] = []
        udp_socket.setblocking(block)
        while True:
            try:
                datagram, address = udp_socket.recvfrom(4096)
                datagrams.append(datagram)
            except BlockingIOError:
                break
            except ConnectionRefusedError:
                break
        for datagram in datagrams:
            packet = parse_packet_bytes(datagram)
            if packet.header.type == HT_INITIAL:
                self.last_peer_address_received = address
            received_log.debug(f"Received: \n{packet}")
            packets.append(packet)
        return packets



    def on_stream_frame_received(self, frame: StreamFrame):
        if not self.is_active_stream(frame.stream_id):
            self.create_stream(1)

        if self.is_active_stream(frame.stream_id):
            stream = self._receive_streams[frame.stream_id]
            if frame.offset != stream.offset:
                stream.buffer(frame)
            else:
                stream.write(frame.data)
            self._receive_streams[frame.stream_id] = stream
        else:
            print(f"Stream ID {frame.stream_id} does not exist.")
            exit(1)




    def extract_ack_frame(self, pkt_number: int) -> bool:
        if pkt_number not in self._sender_side_controller.packets_sent:
            return None
        for frame in self._sender_side_controller.packets_sent[pkt_number].packet.frames:
            if frame.type == FT_ACK:
                return frame
        return None


    

    def remove_from_packets_received(self, packet_nums_acknowledged: list[int]) -> None:
        # This function iterates through the packet nums acknoweledged,
        # and checks whether any of the packets that were acknowledged are
        # ack packets, if they are ack packets, then we remove from our list of received packets,
        # so that we don't double acknowledge packets.
        for pkt_num in packet_nums_acknowledged:
            frame: AckFrame = self.extract_ack_frame(pkt_num)
            if frame is not None:
                pkts_acknowledged = [i for i in range(frame.largest_acknowledged, frame.largest_acknowledged - frame.first_ack_range - 1, -1)]
                for num in pkts_acknowledged:
                    self.packet_numbers_received.remove(num)




    def on_ack_frame_received(self, frame: AckFrame):

        # Calculate packet numbers being acked.
        pkt_nums_acknowledged = [i for i in range(frame.largest_acknowledged, frame.largest_acknowledged-frame.first_ack_range-1, -1)]
        if frame.ack_range_count > 0:
            pn = frame.largest_acknowledged - frame.first_ack_range - 1
            for ackrange in frame.ack_range:
                pn -= ackrange.gap
                pkt_nums_acknowledged += [i for i in range(pn, pn-ackrange.ack_range_length-1, -1)]
        
        self.remove_from_packets_received(pkt_nums_acknowledged)
        self.largest_acknowledged = max(self.largest_acknowledged, max(pkt_nums_acknowledged))

        # This updates the congestion controllers bytes_in_flights and packets_sent state.
        self._sender_side_controller.on_packet_numbers_acked(pkt_nums_acknowledged)

        # Detect and handle packet loss.
        lost_packets = self._sender_side_controller.detect_and_remove_lost_packets(self.largest_acknowledged)
        if lost_packets: # Packet loss detected.
            self._sender_side_controller.on_packet_loss() # Update congestion control state.
            retransmissions = self._packetizer.packetize_retransmissions(lost_packets) # Creates new packets
            self.send_packets(retransmissions) # Retransmits packets.
        # If there is no loss, then continue as normal.




class QUICSenderSideController:
    """
        This is the sender side congestion controller.
    """

    def __init__(self):
        self.congestion_window: int = INITIAL_CONGESTION_WINDOW
        self.bytes_in_flight = 0
        self.slow_start_threshold: float = INFINITY
        self.packets_sent: dict[int, PacketSentInfo] = dict()
        self.congestion_recovery_start_time = 0
        self.sent_time_of_last_loss = 0
    



    def on_packet_loss(self):
        if self.in_recovery(self.sent_time_of_last_loss):
            return
        self.slow_start_threshold = self.congestion_window / 2
        self.congestion_window = max(self.slow_start_threshold, MINIMUM_CONGESTION_WINDOW)
        self.congestion_recovery_start_time = time()




    def detect_and_remove_lost_packets(self, largest_acknowledged: int) -> list[PacketSentInfo]:
        # Detecting Loss:
        # A packet is deemed lost if it if ack-eliciting, in-flight, and was sent prior to an acknowledged packet.
        # AND
        # The packet was sent K packets before an acknowledged packet.
        lost_packets: list[PacketSentInfo] = []
        for pkt_num in self.packets_sent:
            packet_is_lost = pkt_num < largest_acknowledged and self.packets_sent[pkt_num].ack_eliciting and self.packets_sent[pkt_num].in_flight and (largest_acknowledged - pkt_num) >= 3
            if packet_is_lost:                               # If the packet is deemed lost.
                lost_packets.append(self.packets_sent[pkt_num])      # Add to lost packets list.
        if lost_packets:
            self.sent_time_of_last_loss = 0
            for lost_packet in lost_packets:
                self.packets_sent.pop(lost_packet.packet_number)
                if lost_packet.in_flight:
                    self.bytes_in_flight -= lost_packet.sent_bytes
                    self.sent_time_of_last_loss = max(self.sent_time_of_last_loss, lost_packet.time_sent)
            if self.sent_time_of_last_loss != 0:
                self.on_packet_loss()
        return lost_packets




    def on_packet_numbers_acked(self, packet_numbers: list[int]) -> None:

        # We only want to process packet numbers that still need to be processed.
        packet_numbers = [x for x in packet_numbers if x in self.packets_sent]

        for x in packet_numbers:
            if not self.packets_sent[x].in_flight:
                # packets that aren't in flight don't count toward cwnd or bytes_in_flight.
                self.packets_sent.pop(x)
                continue
            self.bytes_in_flight -= self.packets_sent[x].sent_bytes
            if self.in_recovery(self.packets_sent[x].time_sent):
                # recovery state, don't increase congestion window.
                self.packets_sent.pop(x)
                continue
            if self.in_slow_start():
                # slow start
                # increase congestion window by bytes acked.
                self.congestion_window += self.packets_sent[x].sent_bytes
            else:
                # congestion avoidance
                # Additive increase, multiplicitive decrease
                self.congestion_window += MAX_DATAGRAM_SIZE * self.packets_sent[x].sent_bytes / self.congestion_window
            self.packets_sent.pop(x)




    def in_recovery(self, time_sent: float) -> bool:
        return time_sent <= self.congestion_recovery_start_time




    def send_packet_cc(self, packet: Packet, udp_socket: socket, connection_context: ConnectionContext) -> None:
        # Send packets based on the internal congestion control state.
        udp_socket.sendto(packet.raw(), connection_context.get_peer_address())
        self.bytes_in_flight += len(packet.raw())
        self.packets_sent[packet.header.packet_number] = PacketSentInfo(time_sent=time(), 
                                                                    in_flight=True,
                                                                    ack_eliciting=True,
                                                                    sent_bytes=len(packet.raw()), 
                                                                    packet_number=packet.header.packet_number,
                                                                    packet=packet)




    def send_non_ack_eliciting_packet(self, packet: Packet, udp_socket: socket, connection_context: ConnectionContext) -> None:
        # For non-ack eliciting packets we don't care about congestion control state.
        udp_socket.sendto(packet.raw(), connection_context.get_peer_address())
        self.packets_sent[packet.header.packet_number] = PacketSentInfo(time_sent=time(), 
                                                                    in_flight=False,
                                                                    ack_eliciting=False,
                                                                    sent_bytes=len(packet.raw()), 
                                                                    packet_number=packet.header.packet_number,
                                                                    packet=packet)




    def can_send(self):
        return self.bytes_in_flight < self.congestion_window




    def in_slow_start(self) -> bool:
        return self.congestion_window < self.slow_start_threshold

