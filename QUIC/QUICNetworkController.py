from .QUICPacketParser import parse_packet_bytes, PacketParserError
from .QUICPacket import *
from .QUICConnection import ConnectionContext
from socket import socket
UDPSocket = socket

# Congestion Controller States
SLOW_START = 1
RECOVERY = 2
CONGESTION_AVOIDANCE = 3

# Congestion Controller Data
INITIAL_SLOW_START_THRESHOLD = float('inf')
MAX_DATAGRAM_SIZE = 65507
SAFE_DATAGRAM_PAYLOAD_SIZE = 512 # bytes
INITIAL_CONGESTION_WINDOW = MAX_DATAGRAM_SIZE*10 # Initial window is 10 times max datagram size RFC 9002
MINIMUM_CONGESTION_WINDOW = MAX_DATAGRAM_SIZE*2  # Minimum window is 2 times max datagram size RFC 9002

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
    

    def packetize_acknowledgement(self, packet: Packet, connection_context: ConnectionContext) -> Packet:
        pass


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
        self._connection_context: ConnectionContext | None = None
        self._sender_side_controller = QUICSenderSideController()
        self._packetizer = QUICPacketizer()
        self._receive_streams = dict() # Key: Stream ID (int) | Value: Stream object
        self._send_streams = dict()
        self.buffered_packets = []


    def set_connection_state(self, connection_context: ConnectionContext) -> None:
        self._connection_context = connection_context
    

    def get_connection_state(self) -> ConnectionContext:
        return self._connection_context 


    def create_stream(self, stream_id: int) -> None:
        self._receive_streams[stream_id] = ReceiveStream(stream_id=stream_id)
        self._send_streams[stream_id] = SendStream(stream_id=stream_id)


    def send_stream_data(self, stream_id: int, data: bytes, udp_socket: socket):
        # Check for new packets to process and process them.
        packets_to_process = self.receive_new_packets(udp_socket)
        self.process_packets(packets_to_process)

        # Packetize the stream data.
        packets: list[Packet] = self._packetizer.packetize_stream_data(stream_id, data, self._connection_context, self._send_streams)
        # Add the currently buffered packets to the list of packets to send.
        packets = packets + self.buffered_packets
        self.buffered_packets = []

        # TODO: Implement invoking the sendersidecontroller to send the packets.
        self._sender_side_controller.send_packets(packets, udp_socket, self._connection_context)


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
            self.process_packets(packets)
            stream = self._receive_streams[stream_id]
            data += stream.read(num_bytes)
            self._receive_streams[stream_id] = stream
            if data:
                data_not_read = False
        return data


    def receive_new_packets(self, socket: UDPSocket, block=False):
        packets: list[Packet] = []
        datagrams: list[bytes] = []
        socket.setblocking(block)
        while True:
            try:
                datagram, _ = socket.recvfrom(4096)
                datagrams.append(datagram)
            except BlockingIOError:
                break
        for datagram in datagrams:
            packet = parse_packet_bytes(datagram)
            packets.append(packet)
        return packets


    def is_active_stream(self, stream_id: int) -> bool:
        return stream_id in self._receive_streams


    def is_ack_eliciting(self, packet: Packet) -> bool:
        for frame in packet.frames:
            if frame.type not in [FT_ACK, FT_PADDING, FT_CONNECTIONCLOSE]:
                return True
        return False


    def send_acknowledgement(self, packet: Packet) -> None:
        pass


    def process_short_header_packet(self, packet: Packet) -> None:

        if self.is_ack_eliciting(packet):
            self.acknowledge(packet)

        for frame in packet.frames:
            if frame.type == FT_STREAM:
                frame: StreamFrame = frame
                if self.is_active_stream(frame.stream_id):
                    stream = self._receive_streams[frame.stream_id]
                    if frame.offset != stream.offset:
                        stream.buffer(frame)
                    else:
                        stream.write(frame.data)
                    self._receive_streams[frame.stream_id] = stream
                else:
                    # If the stream doesn't exist, then discard the frame.
                    continue
            if frame.type == FT_ACK:
                # TODO: implement code for handling ack frames.
                pass
            # TODO: Add checks for other frame types i.e. StreamClose, ConnectionClose, etc.
    

    def process_long_header_packet(self, packet: Packet) -> None:
        # TODO: Implement long header packet processing logic.
        pass


    def process_packets(self, packets: list[Packet]) -> None:
        # TODO: Implement processing packet logic.
        for packet in packets:
            # Packets could be short header or long header.
            # Short header packets would indicate stream data or acks.
            # Long header packets indicate control operations.
            if packet.header.type == HT_DATA: # If short header
                self.process_short_header_packet(packet)
            elif packet.header.type in [HT_INITIAL, HT_HANDSHAKE, HT_RETRY]:
                self.process_long_header_packet(packet)
    

    # ------- Congestion Control Events --------------

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


    def on_acknowledgement(self):
        # Routine that is run in response to acknowledgment.
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
        self._unacknowledged_packets: list[Packet] = []
        self.sender_state: int = SLOW_START
        self.congestion_window: int = INITIAL_CONGESTION_WINDOW
        self.slow_start_threshold: int = INITIAL_SLOW_START_THRESHOLD # Initially set to infinity.
        self.bytes_in_flight = 0
        self.loss_epoch: float = 0.0
        self.send_time_of_largested_acked: float = 0.0
        self.min_rtt: float = float('inf')
        self.smoothed_rtt: float = 0.0
        self.rtt_var: float = 0.0


    def send_packets(self, packets: list[Packet], udp_socket: socket, connection_context: ConnectionContext) -> None:
        # Send packets based on the internal congestion control state.
        for packet in packets:
            if self.bytes_in_flight < self.congestion_window:
                udp_socket.sendto(packet.raw(), connection_context.get_peer_address())
                self.bytes_in_flight += len(packet.raw())
            else:
                # Need to receive new packets and alter congestion control state.
                # 1. Acked packets will reduce bytes in flight which will allow more packets to be sent.
                # 2. Packet loss will possibly reduce the congestion window further, etc.
                # 3. 
                pass


    def is_in_slow_start(self) -> bool:
        if self.congestion_window < self.slow_start_threshold:
            return True
        return False


    def calculate_rtt_sample(self, ack_time: int) -> float:
        latest_rrt = ack_time - self.send_time_of_largest_acked
        if latest_rrt < self.min_rtt: 
            self.min_rtt = latest_rrt
        return latest_rrt

