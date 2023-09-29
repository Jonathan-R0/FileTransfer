import logging
from lib.common.config import DATA_SIZE
from io import BufferedReader, BufferedWriter

class FileHandler:

    def __init__(self, file: BufferedReader | BufferedWriter, chunk_size: int = DATA_SIZE):
        self.file = file
        self.chunk_size = chunk_size

    def read_next_chunk(self, seq: int) -> tuple[bytes, bool]:
        self.file.seek((seq - 1) * self.chunk_size)
        chunk = self.file.read(self.chunk_size)
        logging.debug(f' Read chunk {chunk} with size: {len(chunk)}')
        return chunk, len(chunk) < self.chunk_size

    def append_chunk(self, chunk: bytes) -> None:
        self.file.write(chunk)

    def close(self):
        self.file.close()
