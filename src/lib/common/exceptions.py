class DownloadingTemporaryFileError(Exception):
    def __init__(self):
        super().__init__(self.message)