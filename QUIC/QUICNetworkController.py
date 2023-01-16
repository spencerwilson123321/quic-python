from .QUICPacketParser import parse_packet_bytes, PacketParserError


# Congestion Controller States
SLOW_START = 1
RECOVERY = 2
CONGESTION_AVOIDANCE = 3

# Congestion Controller Data
INITIAL_SLOW_START_THRESHOLD = float('inf')
MAX_DATAGRAM_SIZE = 65507
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
        self._receiver_side_controller = QUICReceiverSideController()
        self._sender_side_controller = QUICSenderSideController()


    def send_stream_data(self):
        pass


class QUICReceiverSideController:
    """
        This class needs a function that reads all datagrams from the UDP socket buffer, and converts them into QUIC packets
        and then returns the QUIC packets so that they can be processed by the NetworkController.
    """

    def __init__(self):
        pass

    def retrieve_all_quic_packets(self):
        packets = []

        return packets


class QUICSenderSideController:
    """
        This is the sender side congestion controller.
    """

    def __init__(self):
        self.sender_state = SLOW_START
        self.congestion_window = INITIAL_CONGESTION_WINDOW
        self.slow_start_threshold = INITIAL_SLOW_START_THRESHOLD # Initially set to infinity.
        self.loss_epoch = 0
        self.send_time_of_largested_acked = 0
        self.min_rtt = float('inf') # Must be set to the first rtt sample and then set to the lesser of latest_rtt and min_rtt on all other samples.
        self.smoothed_rtt = 0
        self.rtt_var = 0


    def is_in_slow_start(self):
        if self.congestion_window < self.slow_start_threshold:
            return True
        return False


    def calculate_rtt_sample(self, ack_time: int):
        latest_rrt = ack_time - self.send_time_of_largest_acked
        if latest_rrt < self.min_rtt: 
            self.min_rtt = latest_rrt
        return latest_rrt

