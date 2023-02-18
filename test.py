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
        nc.on_stream_frame_received(f1)
        nc.on_stream_frame_received(f2)
        nc.on_stream_frame_received(f3)
        self.assertEqual(nc._receive_streams[1].data, b"0123456789abcde") 

        f1 = StreamFrame(stream_id=1, offset=0, length=5, data=b"01234")
        f3 = StreamFrame(stream_id=1, offset=10, length=5, data=b"abcde")
        f2 = StreamFrame(stream_id=1, offset=5, length=5, data=b"56789")
        nc = QUICNetworkController()
        nc.create_stream(1)
        nc.on_stream_frame_received(f1)
        nc.on_stream_frame_received(f2)
        nc.on_stream_frame_received(f3)
        self.assertEqual(nc._receive_streams[1].data, b"0123456789abcde") 

        f3 = StreamFrame(stream_id=1, offset=10, length=5, data=b"abcde")
        f2 = StreamFrame(stream_id=1, offset=5, length=5, data=b"56789")
        f1 = StreamFrame(stream_id=1, offset=0, length=5, data=b"01234")
        nc = QUICNetworkController()
        nc.create_stream(1)
        nc.on_stream_frame_received(f1)
        nc.on_stream_frame_received(f2)
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
        self.assertEquals(False, msg == encrypted)
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
