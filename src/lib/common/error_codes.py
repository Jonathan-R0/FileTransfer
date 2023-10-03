import logging

FILE_NOT_FOUND_ERROR_CODE = 1
FILE_OPENING_OS_ERROR_CODE = 2
FILE_ALREADY_EXISTS_ERROR_CODE = 3


def handle_error_codes_client(error_code: int) -> None:
    if error_code == FILE_NOT_FOUND_ERROR_CODE:
        logging.debug("The file you are trying to download does not exist")
    if error_code == FILE_OPENING_OS_ERROR_CODE:
        logging.debug("The file you are trying to download cannot be opened")
    if error_code == FILE_ALREADY_EXISTS_ERROR_CODE:
        logging.debug("The file you are trying to upload already exists")
    else:
        logging.debug("An unknown error has occurred")
