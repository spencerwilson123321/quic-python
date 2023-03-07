import unittest
from QUIC import *
from database import Database
from os import system


class TestNetworkController(unittest.TestCase):

    def test_packetize_acknowledgement(self):
        packetizer = QUICPacketizer()
        context = ConnectionContext()
        i2 = [1, 2, 3, 6, 7, 8, 9, 13, 14, 15, 18, 19]
        pkt = packetizer.packetize_acknowledgement(connection_context=context, packet_numbers_received=i2)
        

    def test_on_ack_frame_received(self):
        nc = QUICNetworkController()
        ack = AckFrame(largest_acknowledged=13, first_ack_range=5, ack_delay=0, ack_range_count=1, ack_range=[AckRange(gap=3, ack_range_length=2)])
    

    def test_is_ack_eliciting(self):
        nc = QUICNetworkController()

        frame = AckFrame(largest_acknowledged=13, first_ack_range=5, ack_delay=0, ack_range_count=1, ack_range=[AckRange(gap=3, ack_range_length=2)])
        hdr = ShortHeader(destination_connection_id=0, packet_number=1)
        pkt = Packet(header=hdr, frames=[frame])
        self.assertEqual(nc.is_ack_eliciting(pkt), False)

        frame = ConnectionCloseFrame(error_code=1, reason_phrase_len=5, reason_phrase=b"12345")
        hdr = ShortHeader(destination_connection_id=0, packet_number=1)
        pkt = Packet(header=hdr, frames=[frame])
        self.assertEqual(nc.is_ack_eliciting(pkt), False)

        frame = StreamFrame(stream_id=1, offset=0, length=5, data=b"12345")
        hdr = ShortHeader(destination_connection_id=0, packet_number=1)
        pkt = Packet(header=hdr, frames=[frame])
        self.assertEqual(nc.is_ack_eliciting(pkt), True)


    def test_is_active_stream(self):
        nc = QUICNetworkController()
        self.assertEqual(nc.is_active_stream(1), False)
        nc.create_stream(1)
        self.assertEqual(nc.is_active_stream(1), True)


    def test_on_stream_frame_received(self):
        f1 = StreamFrame(stream_id=1, offset=0, length=5, data=b"01234")
        f2 = StreamFrame(stream_id=1, offset=5, length=5, data=b"56789")
        f3 = StreamFrame(stream_id=1, offset=10, length=5, data=b"abcde")
        nc = QUICNetworkController()
        nc.create_stream(1)
        nc.on_stream_frame_received(f2)
        nc.on_stream_frame_received(f3)
        nc.on_stream_frame_received(f1)
        self.assertEqual(nc._receive_streams[1].data, b"0123456789abcde") 

        f1 = StreamFrame(stream_id=1, offset=0, length=5, data=b"01234")
        f3 = StreamFrame(stream_id=1, offset=10, length=5, data=b"abcde")
        f2 = StreamFrame(stream_id=1, offset=5, length=5, data=b"56789")
        nc = QUICNetworkController()
        nc.create_stream(1)
        nc.on_stream_frame_received(f2)
        nc.on_stream_frame_received(f1)
        nc.on_stream_frame_received(f3)
        self.assertEqual(nc._receive_streams[1].data, b"0123456789abcde") 

        f3 = StreamFrame(stream_id=1, offset=10, length=5, data=b"abcde")
        f2 = StreamFrame(stream_id=1, offset=5, length=5, data=b"56789")
        f1 = StreamFrame(stream_id=1, offset=0, length=5, data=b"01234")
        nc = QUICNetworkController()
        nc.create_stream(1)
        nc.on_stream_frame_received(f2)
        nc.on_stream_frame_received(f1)
        nc.on_stream_frame_received(f3)
        self.assertEqual(nc._receive_streams[1].data, b"0123456789abcde") 




class TestQUICPacket(unittest.TestCase):
    
    def test_long_header(self):

        # Testing destination connection ID parameter.
        with self.assertRaises(InvalidArgumentException):
            header = LongHeader(type=HT_INITIAL, destination_connection_id=1239810293810832, source_connection_id=1023, packet_number=1)

        with self.assertRaises(InvalidArgumentException):
            header = LongHeader(type=HT_HANDSHAKE, destination_connection_id=1023, source_connection_id=-123123, packet_number=1)
        
        with self.assertRaises(InvalidArgumentException):
            header = LongHeader(type=HT_HANDSHAKE, destination_connection_id=-1, source_connection_id=-123123, packet_number=1)


        # Testing header type parameter.
        with self.assertRaises(InvalidArgumentException):
            header = LongHeader(type=1232, destination_connection_id=1023, source_connection_id=1023, packet_number=1)

        with self.assertRaises(InvalidArgumentException):
            header = LongHeader(type=None, destination_connection_id=1023, source_connection_id=1023, packet_number=1)

        # Testing source connection_id parameter.
        with self.assertRaises(TypeError):
            header = LongHeader(type=HT_INITIAL, destination_connection_id=1023, source_connection_id="hello", packet_number=1)

        with self.assertRaises(TypeError):
            header = LongHeader(type=HT_INITIAL, destination_connection_id=1023, source_connection_id=None, packet_number=1)
    

    def test_short_header(self):
        """
            This tests different combinations of parameters for the short header class.
        """
        # Testing destination_connection_id integer parameters that are invalid.
        self.assertRaises(InvalidArgumentException, ShortHeader, destination_connection_id=-1, packet_number=1)
        self.assertRaises(InvalidArgumentException, ShortHeader, destination_connection_id=1409128301928301923, packet_number=1)

        # Testing packet_number integer parameters that are invalid.
        self.assertRaises(InvalidArgumentException, ShortHeader, destination_connection_id=1023, packet_number=-11)
        self.assertRaises(InvalidArgumentException, ShortHeader, destination_connection_id=1023, packet_number=1123123123123123)
        
        # Testing incorrect types for destination_connection_id.
        self.assertRaises(TypeError, ShortHeader, destination_connection_id=None, packet_number=1)
        self.assertRaises(TypeError, ShortHeader, destination_connection_id="", packet_number=1)
        self.assertRaises(TypeError, ShortHeader, destination_connection_id=b"", packet_number=1)
        self.assertRaises(TypeError, ShortHeader, destination_connection_id=True, packet_number=1)

        # Testing incorrect types for packet_number.
        self.assertRaises(TypeError, ShortHeader, destination_connection_id=1023, packet_number=None)
        self.assertRaises(TypeError, ShortHeader, destination_connection_id=1023, packet_number="")
        self.assertRaises(TypeError, ShortHeader, destination_connection_id=1023, packet_number=b"")
        self.assertRaises(TypeError, ShortHeader, destination_connection_id=1023, packet_number=True)
        

    def test_stream_frame(self):

        StreamFrame(stream_id=1, offset=10, length=10, data=b"1234567890")

        # Trying incorrect types for length parameter.
        self.assertRaises(TypeError, StreamFrame, stream_id=1, offset=10, length=True, data=b"")
        self.assertRaises(TypeError, StreamFrame, stream_id=1, offset=10, length="", data=b"")
        self.assertRaises(TypeError, StreamFrame, stream_id=1, offset=10, length=b"", data=b"")
        self.assertRaises(TypeError, StreamFrame, stream_id=1, offset=10, length=123.123, data=b"")

        # Trying incorrect types for offset parameter.
        self.assertRaises(TypeError, StreamFrame, stream_id=1, offset=True, length=10, data=b"")
        self.assertRaises(TypeError, StreamFrame, stream_id=1, offset="", length=10, data=b"")
        self.assertRaises(TypeError, StreamFrame, stream_id=1, offset=b"", length=10, data=b"")
        self.assertRaises(TypeError, StreamFrame, stream_id=1, offset=123.123, length=10, data=b"")
        
        # Trying incorrect types for stream_id parameter.
        self.assertRaises(TypeError, StreamFrame, stream_id=True, offset=10, length=10, data=b"")
        self.assertRaises(TypeError, StreamFrame, stream_id="", offset=10, length=10, data=b"")
        self.assertRaises(TypeError, StreamFrame, stream_id=b"", offset=10, length=10, data=b"")
        self.assertRaises(TypeError, StreamFrame, stream_id=123.123, offset=10, length=10, data=b"")
        
        # Trying incorrect types for stream_id parameter.
        self.assertRaises(TypeError, StreamFrame, stream_id=1, offset=10, length=10, data=True)
        self.assertRaises(TypeError, StreamFrame, stream_id=1, offset=10, length=10, data="")
        self.assertRaises(TypeError, StreamFrame, stream_id=1, offset=10, length=10, data=123.123)
        self.assertRaises(TypeError, StreamFrame, stream_id=1, offset=10, length=10, data=123)
        
        # Trying negative values for integer parameters.
        self.assertRaises(InvalidArgumentException, StreamFrame, stream_id=-1, offset=10, length=10, data=b"")
        self.assertRaises(InvalidArgumentException, StreamFrame, stream_id=1, offset=-1, length=10, data=b"")
        self.assertRaises(InvalidArgumentException, StreamFrame, stream_id=1, offset=10, length=-1, data=b"")

        # Trying too large integer values for integer parameters.
        self.assertRaises(InvalidArgumentException, StreamFrame, stream_id=256, offset=10, length=10, data=b"")
        self.assertRaises(InvalidArgumentException, StreamFrame, stream_id=1, offset=10981029381093280918123123123, length=10, data=b"")
        self.assertRaises(InvalidArgumentException, StreamFrame, stream_id=1, offset=10, length=65536, data=b"")


    def test_crypto_frame(self):
        CryptoFrame(offset=10, length=10, data=b"")

        # Trying negative values for offset
        self.assertRaises(InvalidArgumentException, CryptoFrame, offset=-10, length=13, data=b"")

        # Trying negative values for length.
        self.assertRaises(InvalidArgumentException, CryptoFrame, offset=10, length=-13, data=b"")
    
        # Trying too large value for offset.
        self.assertRaises(InvalidArgumentException, CryptoFrame, offset=123123123123123123123123, length=13, data=b"")

        # Trying too large value for length.
        self.assertRaises(InvalidArgumentException, CryptoFrame, offset=12, length=23123123123, data=b"")

        # Trying incorrect types for offset.
        self.assertRaises(TypeError, CryptoFrame, offset=b"", length=13, data=b"")
        self.assertRaises(TypeError, CryptoFrame, offset="", length=13, data=b"")
        self.assertRaises(TypeError, CryptoFrame, offset=10.123, length=13, data=b"")
        self.assertRaises(TypeError, CryptoFrame, offset=True, length=13, data=b"")

        # Incorrect types for length.
        self.assertRaises(TypeError, CryptoFrame, offset=10, length=b"", data=b"")
        self.assertRaises(TypeError, CryptoFrame, offset=10, length="", data=b"")
        self.assertRaises(TypeError, CryptoFrame, offset=10, length=10.123, data=b"")
        self.assertRaises(TypeError, CryptoFrame, offset=10, length=True, data=b"")

        # Incorrect types for data.
        self.assertRaises(TypeError, CryptoFrame, offset=10, length=10, data="")
        self.assertRaises(TypeError, CryptoFrame, offset=10, length=10, data=123)
        self.assertRaises(TypeError, CryptoFrame, offset=10, length=10, data=123.123)
        self.assertRaises(TypeError, CryptoFrame, offset=10, length=10, data=True)


    def test_ack_frame(self):
        # self.assertRaises(InvalidArgumentException, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=0, first_ack_range=0, ack_range=[])
        # self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=0, first_ack_range=0, ack_range=[])
        
        # Negative values, large values
        self.assertRaises(InvalidArgumentException, AckFrame, largest_acknowledged=-1, ack_delay=1, ack_range_count=0, first_ack_range=0, ack_range=[])
        self.assertRaises(InvalidArgumentException, AckFrame, largest_acknowledged=123123123123, ack_delay=1, ack_range_count=0, first_ack_range=0, ack_range=[])

        self.assertRaises(InvalidArgumentException, AckFrame, largest_acknowledged=1, ack_delay=-1, ack_range_count=0, first_ack_range=0, ack_range=[])
        self.assertRaises(InvalidArgumentException, AckFrame, largest_acknowledged=1, ack_delay=11231231231231123, ack_range_count=0, first_ack_range=0, ack_range=[])

        self.assertRaises(InvalidArgumentException, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=-1, first_ack_range=0, ack_range=[])
        self.assertRaises(InvalidArgumentException, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=123123123123123123, first_ack_range=0, ack_range=[])
        
        self.assertRaises(InvalidArgumentException, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=0, first_ack_range=-1, ack_range=[])
        self.assertRaises(InvalidArgumentException, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=0, first_ack_range=1231231231231231213, ack_range=[])

        # Incorrect types
        self.assertRaises(TypeError, AckFrame, largest_acknowledged="", ack_delay=1, ack_range_count=0, first_ack_range=1, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=b"", ack_delay=1, ack_range_count=0, first_ack_range=1, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=None, ack_delay=1, ack_range_count=0, first_ack_range=1, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=123.123, ack_delay=1, ack_range_count=0, first_ack_range=1, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=True, ack_delay=1, ack_range_count=0, first_ack_range=1, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=[], ack_delay=1, ack_range_count=0, first_ack_range=1, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=set(), ack_delay=1, ack_range_count=0, first_ack_range=1, ack_range=[])
        
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay="", ack_range_count=0, first_ack_range=1, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=b"", ack_range_count=0, first_ack_range=1, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=None, ack_range_count=0, first_ack_range=1, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=123.123, ack_range_count=0, first_ack_range=1, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=True, ack_range_count=0, first_ack_range=1, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=[], ack_range_count=0, first_ack_range=1, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay={}, ack_range_count=0, first_ack_range=1, ack_range=[])

        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count="", first_ack_range=0, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=b"", first_ack_range=0, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=None, first_ack_range=0, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=123.123, first_ack_range=0, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=True, first_ack_range=0, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=[], first_ack_range=0, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count={}, first_ack_range=0, ack_range=[])

        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=0, first_ack_range="", ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=0, first_ack_range=b"", ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=0, first_ack_range=None, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=0, first_ack_range=123.123, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=0, first_ack_range=False, ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=0, first_ack_range=[], ack_range=[])
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=0, first_ack_range={}, ack_range=[])

        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=0, first_ack_range=0, ack_range="")
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=0, first_ack_range=0, ack_range=b"")
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=0, first_ack_range=0, ack_range=None)
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=0, first_ack_range=0, ack_range=12)
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=0, first_ack_range=0, ack_range=123.123)
        self.assertRaises(TypeError, AckFrame, largest_acknowledged=1, ack_delay=1, ack_range_count=0, first_ack_range=0, ack_range={})



    def test_ack_range(self):
        
        # Trying negative values for gap and ack_range_length
        self.assertRaises(InvalidArgumentException, AckRange, gap=-1, ack_range_length=10)
        self.assertRaises(InvalidArgumentException, AckRange, gap=1, ack_range_length=-10)

        # Trying large values for gap and ack_range_length
        self.assertRaises(InvalidArgumentException, AckRange, gap=123123123123123, ack_range_length=10)
        self.assertRaises(InvalidArgumentException, AckRange, gap=1, ack_range_length=123123123123123)

        # Incorrect types for gap.
        self.assertRaises(TypeError, AckRange, gap="", ack_range_length=10)
        self.assertRaises(TypeError, AckRange, gap=b"", ack_range_length=10)
        self.assertRaises(TypeError, AckRange, gap=None, ack_range_length=10)
        self.assertRaises(TypeError, AckRange, gap=123.123, ack_range_length=10)

        # Incorrect types for ack_range_length.
        self.assertRaises(TypeError, AckRange, gap=1, ack_range_length="")
        self.assertRaises(TypeError, AckRange, gap=1, ack_range_length=b"")
        self.assertRaises(TypeError, AckRange, gap=1, ack_range_length=None)
        self.assertRaises(TypeError, AckRange, gap=1, ack_range_length=123.123)
        self.assertRaises(TypeError, AckRange, gap=1, ack_range_length=dict())
        self.assertRaises(TypeError, AckRange, gap=1, ack_range_length=[])


    def test_padding_frame(self):
        frame = PaddingFrame()
        self.assertEqual(FT_PADDING, frame.type)


    def test_connection_close_frame(self):
        
        # Testing negative values and large values for error_code and reason_phrase_len
        self.assertRaises(InvalidArgumentException, ConnectionCloseFrame, error_code=-1, reason_phrase_len=1, reason_phrase=b"")
        self.assertRaises(InvalidArgumentException, ConnectionCloseFrame, error_code=1, reason_phrase_len=-1, reason_phrase=b"")
        self.assertRaises(InvalidArgumentException, ConnectionCloseFrame, error_code=12312123123, reason_phrase_len=1, reason_phrase=b"")
        self.assertRaises(InvalidArgumentException, ConnectionCloseFrame, error_code=1, reason_phrase_len=123123123123, reason_phrase=b"")
        
        # Testing incorrect types for all parameters.
        self.assertRaises(TypeError, ConnectionCloseFrame, error_code="", reason_phrase_len=1, reason_phrase=b"")
        self.assertRaises(TypeError, ConnectionCloseFrame, error_code=b"", reason_phrase_len=1, reason_phrase=b"")
        self.assertRaises(TypeError, ConnectionCloseFrame, error_code=True, reason_phrase_len=1, reason_phrase=b"")
        self.assertRaises(TypeError, ConnectionCloseFrame, error_code=None, reason_phrase_len=1, reason_phrase=b"")
        self.assertRaises(TypeError, ConnectionCloseFrame, error_code=[], reason_phrase_len=1, reason_phrase=b"")
        self.assertRaises(TypeError, ConnectionCloseFrame, error_code={}, reason_phrase_len=1, reason_phrase=b"")
        self.assertRaises(TypeError, ConnectionCloseFrame, error_code=set(), reason_phrase_len=1, reason_phrase=b"")
        self.assertRaises(TypeError, ConnectionCloseFrame, error_code=123.123, reason_phrase_len=1, reason_phrase=b"")

        self.assertRaises(TypeError, ConnectionCloseFrame, error_code=1, reason_phrase_len="", reason_phrase=b"")
        self.assertRaises(TypeError, ConnectionCloseFrame, error_code=1, reason_phrase_len=b"", reason_phrase=b"")
        self.assertRaises(TypeError, ConnectionCloseFrame, error_code=1, reason_phrase_len=True, reason_phrase=b"")
        self.assertRaises(TypeError, ConnectionCloseFrame, error_code=1, reason_phrase_len=None, reason_phrase=b"")
        self.assertRaises(TypeError, ConnectionCloseFrame, error_code=1, reason_phrase_len=[], reason_phrase=b"")
        self.assertRaises(TypeError, ConnectionCloseFrame, error_code=1, reason_phrase_len={}, reason_phrase=b"")
        self.assertRaises(TypeError, ConnectionCloseFrame, error_code=1, reason_phrase_len=set(), reason_phrase=b"")
        self.assertRaises(TypeError, ConnectionCloseFrame, error_code=1, reason_phrase_len=123.123, reason_phrase=b"")
        

class TestEncryptionContext(unittest.TestCase):

    def test_encryption_context(self):
        TEST_KEY = token_bytes(32)
        msg = b"This is a message."
        encrypted = None

        ec = EncryptionContext(key=TEST_KEY)
        
        self.assertEqual(TEST_KEY, ec.key)
        self.assertEqual(True, type(ec.algorithm) == algorithms.ChaCha20)
        self.assertEqual(True, nonce == ec.nonce)

        encrypted = ec.encrypt(msg)
        self.assertEqual(False, msg == encrypted)
        decrypted = ec.decrypt(encrypted)
        self.assertEqual(True, msg == decrypted)


TEST_DB = "./test_database.txt"

class TestDatabase(unittest.TestCase):

    def test_exists(self):
        from os.path import isfile

        # Remove the test_database file.
        system(f"rm {TEST_DB}")
        # The file should not exist.
        self.assertEqual(False, isfile(TEST_DB))

        # Create database.
        db = Database(filepath=TEST_DB)

        # Does the file get created when the db instance is made?
        self.assertEqual(True, isfile(TEST_DB))

        # Exist
        self.assertEqual(False, db.exists("spencer", "password"))

        # Add user.
        self.assertEqual(True, db.add("spencer", "password"))
        self.assertEqual(True, db.exists("spencer", "password"))
        self.assertEqual(False, db.add("spencer", "password"))

        # Remove user.
        self.assertEqual(True, db.remove("spencer", "password"))
        self.assertEqual(False, db.exists("spencer", "password"))
        self.assertEqual(False, db.remove("spencer", "password"))

        # Clear database. 
        self.assertEqual(True, db.add("spencer", "password"))
        db.clear()
        self.assertEqual(False, db.exists("spencer", "password"))


if __name__ == "__main__":
    unittest.main()
