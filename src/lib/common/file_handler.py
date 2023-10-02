import logging
from lib.common.config import DATA_SIZE
import os


class FileHandler:

    def __init__(
            self,
            filepath: str,
            is_upload: bool,
            mode: str,
            chunk_size: int = DATA_SIZE
            ):
        self.file = open(
            file=(filepath + '.tmp')
            if is_upload and mode == 'wb' else filepath,
            mode=mode)
        self.mode = mode
        self.chunk_size = chunk_size
        self.file.seek(0, os.SEEK_END)
        self.len = self.file.tell()
        self.file.seek(0)
        self.is_upload = is_upload

    def read_next_chunk(self, seq: int) -> tuple[bytes, bool]:
        self.file.seek((seq - 1) * self.chunk_size)
        chunk = self.file.read(self.chunk_size)
        #logging.debug(f' Read chunk {chunk} with size: {len(chunk)}')
        return chunk, len(chunk) < self.chunk_size or \
            len(self.file.read(self.chunk_size)) == 0

    def append_chunk(self, chunk: bytes) -> None:
        if len(chunk) == 0:
            return
        try:
            self.file.write(chunk.decode().rstrip('\0').encode())
        except Exception:
            self.file.write(chunk)  # Not a zero ending string.

    def size(self) -> int:
        return self.len

    def rollback_write(self) -> None:
        try:
            os.remove(self.file.name)
        except FileNotFoundError:
            pass

    def close(self):
        name = self.file.name
        self.file.close()
        if self.is_upload and self.mode == 'wb' and os.path.exists(name):
            os.rename(name, name[:-4])
