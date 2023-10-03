from lib.common.config import DATA_SIZE
import os
from lib.common.exceptions import DownloadingTemporaryFileError, UploadExistingFileError


class FileHandler:

    def __init__(
            self,
            filepath: str,
            is_upload: bool,
            mode: str,
            chunk_size: int = DATA_SIZE
            ):
        if mode == 'rb' and filepath.endswith('.tmp') and not is_upload:
            raise DownloadingTemporaryFileError
        if mode == 'wb' and is_upload and is_upload \
            (os.path.exists(filepath) or os.path.exists(filepath + '.tmp')) :
            raise UploadExistingFileError
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
        return chunk, len(chunk) < self.chunk_size or \
            len(self.file.read(self.chunk_size)) == 0

    def append_chunk(self, chunk: bytes, end: bool) -> None:
        if len(chunk) == 0:
            return
        if end:
            chunk = chunk.rstrip(b'\x00')
        self.file.write(chunk)

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
