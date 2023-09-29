from lib.client.upload import Upload
from lib.client.upload_args import uploader_args
import logging

if uploader_args.verbose:
    logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    logging.debug(' Starting upload...')
    upload = Upload((uploader_args.ADDR, uploader_args.PORT), uploader_args.FILEPATH, uploader_args.FILENAME)
    upload.start()
