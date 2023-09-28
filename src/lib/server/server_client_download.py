from lib.common.package import InitialHandshakePackage
from lib.server.server_client import ServerClient
from lib.common.package import AckSeqPackage, NormalPackage
from lib.common.config import *


class ServerClientDownload(ServerClient):
    def __init__(self, initial_package: InitialHandshakePackage, address: bytes | tuple[str, int], dirpath: str):
        super().__init__(initial_package, address, dirpath)

    def start(self) -> None:
        end_flag = False
        seq = 0
        self.create_socket_and_reply_handshake()
        
        while end_flag == False:
            if len(self.separate_file_into_chunks()) == seq:
                end_flag = True
            ack_recieved, seq_recieved = self.send_chunk_sw(self, seq, end_flag)
            while seq_recieved != seq:
                ack_recieved, seq_recieved = self.send_chunk_sw(self, seq, end_flag)
                if seq_recieved == seq:
                    break
            seq += 1
            if end_flag == True:
                break

    def send_chunk_sw(self, seq: int, end_flag: bool) -> tuple[int, int]:
        self.socket.sendto(self.address, NormalPackage.pack_to_send(0, seq, self.separate_file_into_chunks()[seq], end_flag, 0))
        ackseq_data = self.socket.recvfrom(ACK_SEQ_SIZE)
        ack_recieved, seq_recieved = AckSeqPackage.unpack_from_client(ackseq_data)
        return ack_recieved, seq_recieved

