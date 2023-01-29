from .QUICPacketParser import parse_packet_bytes, PacketParserError
from .QUICPacket import *
from .QUICConnection import ConnectionContext, create_connection_id
from .QUICEncryption import EncryptionContext
from socket import socket
import math
from time import time

# Congestion Controller States
SLOW_START = 1
RECOVERY = 2
CONGESTION_AVOIDANCE = 3

# Congestion Controller Data
INFINITY = math.inf
MAX_DATAGRAM_SIZE = 65507
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

# Detecting Loss:
# A packet is deemed lost if it if ack-eliciting, in-flight, and was sent prior to an acknowledged packet.
# AND
# The packet was sent K packets before an acknowledged packet.
# If we do it this way then we don't need to worry as much about estimating rtt values since our implementation
# is synchronous.

class PacketSentInfo:

    def __init__(self, in_flight=False, sent_bytes=0, time_sent=0.0, packet_number=0, ack_eliciting=False):
        self.in_flight: bool = in_flight
        self.sent_bytes: int = sent_bytes
        self.time_sent: float = time_sent
        self.ack_eliciting: bool = ack_eliciting
        self.packet_number: int = packet_number


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


    def packetize_initial_packet(self, connection_context: ConnectionContext) -> Packet:
        hdr = LongHeader(
            type=HT_INITIAL, 
            destination_connection_id=connection_context.get_peer_connection_id(), 
            source_connection_id=connection_context.get_local_connection_id(), 
            packet_number=self.get_next_packet_number())
        frames = [] # TODO Add crypto frames.
        return Packet(header=hdr, frames=frames)




    def packetize_handshake_packet(self, connection_context: ConnectionContext) -> Packet:
        hdr = LongHeader(
            type=HT_HANDSHAKE,
            destination_connection_id=connection_context.get_peer_connection_id(),
            source_connection_id=connection_context.get_local_connection_id(),
            packet_number=self.get_next_packet_number())
        frames = []
        return Packet(header=hdr, frames=frames)




    def packetize_connection_response_packets(self, connection_context: ConnectionContext) -> list[Packet]:
        hdr1 = LongHeader(
            type=HT_INITIAL,
            destination_connection_id=connection_context.get_peer_connection_id(),
            source_connection_id=connection_context.get_local_connection_id(),
            packet_number=self.get_next_packet_number())
        hdr2 = LongHeader(
            type=HT_HANDSHAKE,
            destination_connection_id=connection_context.get_peer_connection_id(),
            source_connection_id=connection_context.get_local_connection_id(),
            packet_number=self.get_next_packet_number())
        frames1 = []
        frames2 = []
        initial, handshake = Packet(header=hdr1, frames=frames1), Packet(header=hdr2, frames=frames2)
        return [initial, handshake]




    def packetize_acknowledgement(self, connection_context: ConnectionContext, packet_numbers_received: list[int]) -> Packet:
        hdr = ShortHeader(
            packet_number=self.get_next_packet_number(),
            destination_connection_id=connection_context.get_peer_connection_id())

        print("Inside packetize_acknowledgement:")
        print(packet_numbers_received)

        # If the received packets list is length 0
        # We cannot create an ack if we haven't received any packets.
        if not packet_numbers_received:
            return None

        # If the received packets list is length 1
        # Create a simple ack frame.
        if len(packet_numbers_received) == 1:
            frames = [AckFrame(largest_acknowledged=packet_numbers_received[0], ack_delay=0, ack_range_count=0, ack_range=[])]
            return Packet(header=hdr, frames=frames)    

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

        frames = [AckFrame(largest_acknowledged=largest_acknowledged, ack_delay=0, ack_range_count=len(ranges), first_ack_range=first_ack_range, ack_range=ranges)]
        pkt = Packet(header=hdr, frames=frames)
        return pkt
        

    def packetize_stream_data(self, stream_id: int, data: bytes, connection_context: ConnectionContext, send_streams: dict) -> list[Packet]:
        packets = []
        MAX_ALLOWED = SAFE_DATAGRAM_PAYLOAD_SIZE-LONG_HEADER_SIZE-STREAM_FRAME_SIZE
        # If the length of this data would go over the safe datagram size - long header size - stream frame size,
        # then we need to split this data into multiple QUIC packets.
        if len(data) > MAX_ALLOWED:
            bytes_written = 0
            while bytes_written < len(data):
                data_chunk = data[0:MAX_ALLOWED]
                hdr = ShortHeader(
                    destination_connection_id=connection_context.get_peer_connection_id(), 
                    packet_number=self.get_next_packet_number())
                frames = [StreamFrame(stream_id=stream_id, offset=send_streams[stream_id].get_offset(), length=len(data_chunk), data=data_chunk)]
                packets.append(Packet(header=hdr, frames=frames))
                send_streams[stream_id].update_offset(len(data_chunk))
                data = data[MAX_ALLOWED:]
                bytes_written += len(data_chunk)
        else:
            hdr = ShortHeader(
                destination_connection_id=connection_context.get_peer_connection_id(), 
                packet_number=self.get_next_packet_number())
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

        # ---- Handshake Data ----
        self.handshake_complete = False
        self.server_initial_received = False
        self.server_handshake_received = False
        self.state = DISCONNECTED
        self.last_peer_address_received = None

        # ---- Acknowledgement Data ----
        self.largest_packet_number_received: int = 0
        self.first_ack_range = 0
        self.ack_range_count = 0
        self.ack_ranges = []
        self.packet_numbers_received: list[int] = []
        self.packets_received: list[Packet] = []




    def is_handshake_complete(self) -> bool:
        return self.server_handshake_received and self.server_initial_received

 


    def set_state(self, state: int) -> None:
        self.state = state




    def get_state(self) -> int:
        return self.state




    def set_connection_state(self, connection_context: ConnectionContext) -> None:
        self._connection_context = connection_context




    def get_connection_state(self) -> ConnectionContext | None:
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
        while not self.is_handshake_complete():
            packets = self.receive_new_packets(udp_socket)
            self.process_packets(packets, udp_socket)
        
        # ---- Connection Complete ----
        self.state = CONNECTED




    def accept_connection(self, udp_socket: socket) -> ConnectionContext:
        if self.state != LISTENING_INITIAL:
            print("Must be in LISTENING state to accept()")
            exit(1)
        while self.state == LISTENING_INITIAL:
            # We are listening for INITIAL packets.
            packets = self.receive_new_packets(udp_socket)
            self.process_packets(packets, udp_socket)
        while self.state == LISTENING_HANDSHAKE:
            packets = self.receive_new_packets(udp_socket)
            self.process_packets(packets, udp_socket)
        self.state = LISTENING_INITIAL
        # After this point the handshake is complete.




    def send_stream_data(self, stream_id: int, data: bytes, udp_socket: socket):
        # Check for new packets to process and process them.
        packets_to_process = self.receive_new_packets(udp_socket)
        self.process_packets(packets_to_process, udp_socket)

        # Packetize the stream data.
        packets: list[Packet] = self._packetizer.packetize_stream_data(stream_id, data, self._connection_context, self._send_streams)
        # Add the currently buffered packets to the list of packets to send.

        # TODO: Implement invoking the sendersidecontroller to send the packets.
        could_not_send: list[Packet] = self.send_packets(packets, udp_socket)
        while could_not_send:
            # Reprocess packets that could not be sent.
            packets_to_process = self.receive_new_packets(udp_socket)
            self.process_packets(packets_to_process, udp_socket)
            could_not_send = self.send_packets(could_not_send, udp_socket)            




    def send_packets(self, packets: list[Packet], udp_socket: socket) -> list[Packet]:
        could_not_send: list[Packet] = []
        for packet in packets:
            print("Sent:\n")
            print(packet)
            if self.is_ack_eliciting(packet):
                # If the packet is ack eliciting,
                # then send it with congestion control.
                if self._sender_side_controller.can_send():
                    # bytes in flight < congestion window
                    self._sender_side_controller.send_packet_cc(packet, udp_socket, self._connection_context)
                else:
                    # bytes in flight >= congestion window
                    # Need to wait to receive more acks before continuing to send.
                    could_not_send.append(packet)
            else:
                # This is an Ack, Padding, or ConnectionClose packet,
                self._sender_side_controller.send_non_ack_eliciting_packet(packet, udp_socket, self._connection_context)
        return could_not_send




    def read_stream_data(self, stream_id: int, num_bytes: int, udp_socket: socket):
        """
            This function will block until at least some data has been read.
        """
        data_not_read = True
        data = b""
        while data_not_read:
            # First, we need to receive all new packets in kernel queue,
            # and process each one.
            packets = self.receive_new_packets(udp_socket)
            self.process_packets(packets, udp_socket)
            stream = self._receive_streams[stream_id]
            data += stream.read(num_bytes)
            self._receive_streams[stream_id] = stream
            if data:
                data_not_read = False
        return data




    def receive_new_packets(self, udp_socket: socket, block=False):
        packets: list[Packet] = []
        datagrams: list[bytes] = []
        udp_socket.setblocking(block)
        while True:
            try:
                datagram, address = udp_socket.recvfrom(4096)
                datagrams.append(datagram)
            except BlockingIOError:
                break
        for datagram in datagrams:
            packet = parse_packet_bytes(datagram)
            if packet.header.type == HT_INITIAL:
                self.last_peer_address_received = address
            packets.append(packet)
        return packets




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




    def update_received_packets(self, packet: Packet) -> None:
        self.packet_numbers_received.append(packet.header.packet_number)
        self.packets_received.append(packet)




    def process_short_header_packet(self, packet: Packet) -> None:
        # Processing Short Header Packet Frames:
        # 1. Stream Frame --> Write to stream or buffer data.
        # 2. Ack Frame    --> Remove from packets_sent, decrement bytes_in_flight, other congestion control stuff.
        for frame in packet.frames:
            if frame.type == FT_STREAM:
                self.on_stream_frame_received(frame)
            if frame.type == FT_ACK:
                self.on_ack_frame_received(frame)
            # TODO: Add checks for other frame types i.e. StreamClose, ConnectionClose, etc.




    def process_long_header_packet(self, packet: Packet, udp_socket: socket) -> None:
        if packet.header.type == HT_INITIAL:
            if self.state == INITIALIZING:
                self._connection_context.set_peer_address(self.last_peer_address_received)
                self._connection_context.set_local_connection_id(packet.header.destination_connection_id)
                self._connection_context.set_peer_connection_id(create_connection_id())
                self.server_initial_received = True
                self.state = INITIALIZING
            if self.state == LISTENING_HANDSHAKE:
                pass
            if self.state == CONNECTED:
                # We can't accept connections while in a connected state.
                return None
            if self.state == DISCONNECTED:
                # Cannot accept connections when not in listening state.
                pass
            if self.state == LISTENING_INITIAL:
                # Incoming connection request.
                # 1. Update connection context with peer address. ip / port
                # 2. Update connection context with peer connection id.
                # 3. Send response packets.
                # 4. Set the state to LISTENING_HANDSHAKE.
                self._connection_context.set_peer_address(self.last_peer_address_received)
                self._connection_context.set_local_connection_id(packet.header.destination_connection_id)
                self._connection_context.set_peer_connection_id(create_connection_id())
                packets = self._packetizer.packetize_connection_response_packets(self._connection_context)
                self.send_packets(packets, udp_socket)
                self.state = LISTENING_HANDSHAKE
        if packet.header.type == HT_HANDSHAKE:
            if self.state == LISTENING_HANDSHAKE:
                # Client is completing the handshake.
                # Only thing left to do is change the state
                # so that we exit the accept_connection loop.
                self.state = CONNECTED
            if self.state == INITIALIZING:
                self.server_handshake_received = True
                if self.server_initial_received:
                    packet = self._packetizer.packetize_handshake_packet(self._connection_context)
                    self.send_packets([packet], udp_socket)
                    self.state = CONNECTED
                else:
                    self.buffered_packets.append(packet)
                    self.state = INITIALIZING
        if packet.header.type == HT_RETRY:
            pass
        return None




    def process_packets(self, packets: list[Packet], udp_socket: socket) -> None:
        packets = packets + self.buffered_packets
        self.buffered_packets = []
        for packet in packets:
            print("Received:")
            print(packet)
            # ---- PROCESS FRAME INFORMATION ----
            # Short Header:
            # 1. Stream Frames
            # 2. Ack Frames
            # Long Header:
            # 1. Crypto Frames
            # 2. Handshake Frames
            # 3. ConnectionClose Frames
            # 4. NewStream Frames
            # etc...
            if packet.header.type == HT_DATA:
                self.process_short_header_packet(packet)
            elif packet.header.type in [HT_INITIAL, HT_HANDSHAKE, HT_RETRY]:
                self.process_long_header_packet(packet, udp_socket)

            # ---- PROCESS HEADER INFORMATION ----
            # 1. Update the largest packet number seen so far.
            # 2. Store which packet numbers have been received.
            # 3. Store which packet numbers are missing.
            # 4. Send acknowledgement if the packet is ack-eliciting.
            self.update_largest_packet_number_received(packet)
            self.update_received_packets(packet)
            if self.is_ack_eliciting(packet):
                self.create_and_send_acknowledgements(udp_socket)




    def on_stream_frame_received(self, frame: StreamFrame):
        if self.is_active_stream(frame.stream_id):
            stream = self._receive_streams[frame.stream_id]
            if frame.offset != stream.offset:
                stream.buffer(frame)
            else:
                stream.write(frame.data)
            self._receive_streams[frame.stream_id] = stream




    def on_packet_loss(self):
        # Routine that is run in response to packet loss.
        # If the congestion controller is in SLOW_START:
            # CongestionController is set to RECOVERY state:
            # 1. Slow Start Threshold is reduced to half of congestion window.
            # 2. Recovery timer is started.
        # If the congestion controller is in RECOVERY already:
            # 1. The congestion window does not change in response to loss when already in recovery.
        # If the congestion controller is in CONGESTION_AVOIDANCE:
            # 1. Slow Start Threshold is reduced to half of congestion window.
            # 2. Recovery timer is started.
        pass




    def on_ack_frame_received(self, frame: AckFrame):
        # 1. Update the sender side controllers' state with the newly acked packets.
        # SLOW_START:
            # 1. Increase congestion window by number of bytes acknowledged.
            # 2. Update bytes in flight.
        # CONGESTION_AVOIDANCE:
            # 1. When a full congestion window of bytes is acknowledged, increase the congestion window by one maximum datagram size.
            # 2. Update bytes in flight.
        # RECOVERY:
            # 1. If the packet being acknowledged was sent during the recovery period, then enter congestion avoidance.
            # 2. If the packet being acknowledged was sent before the recovery period, update bytes in flight.
        pass




class QUICSenderSideController:
    """
        This is the sender side congestion controller.
    """

    def __init__(self):
        self.sender_state: int = SLOW_START
        self.congestion_window: int = INITIAL_CONGESTION_WINDOW
        self.bytes_in_flight = 0
        self.slow_start_threshold: float = INFINITY
        self.packets_sent: dict[int, PacketSentInfo] = dict()


    def send_packet_cc(self, packet: Packet, udp_socket: socket, connection_context: ConnectionContext) -> None:
        # Send packets based on the internal congestion control state.
        udp_socket.sendto(packet.raw(), connection_context.get_peer_address())
        self.bytes_in_flight += len(packet.raw())
        self.packets_sent[packet.header.packet_number] = PacketSentInfo(time_sent=time(), 
                                                                    in_flight=True,
                                                                    ack_eliciting=True,
                                                                    sent_bytes=len(packet.raw()), 
                                                                    packet_number=packet.header.packet_number)


    def send_non_ack_eliciting_packet(self, packet: Packet, udp_socket: socket, connection_context: ConnectionContext) -> None:
        # For non-ack eliciting packets we don't care about congestion control state.
        udp_socket.sendto(packet.raw(), connection_context.get_peer_address())
        self.packets_sent[packet.header.packet_number] = PacketSentInfo(time_sent=time(), 
                                                                    in_flight=False,
                                                                    ack_eliciting=False,
                                                                    sent_bytes=len(packet.raw()), 
                                                                    packet_number=packet.header.packet_number)


    def can_send(self):
        return self.bytes_in_flight < self.congestion_window


    def is_in_slow_start(self) -> bool:
        return self.congestion_window < self.slow_start_threshold

