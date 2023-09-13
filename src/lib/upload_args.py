import argparse

parser = argparse.ArgumentParser(
                prog='upload',
                description='Send a file to a remote host')

group = parser.add_mutually_exclusive_group(required=False)
group.add_argument('-v', '--verbose', action='store_false', help='increase output verbosity')
group.add_argument('-q', '--quiet', action='store_true', help='decrease output verbosity')  
parser.add_argument('-H', '--host', dest='ADDR', help='server IP address')
parser.add_argument('-p', '--port', dest='PORT', type=int, default=80, help='server port')
parser.add_argument('-s', '--src', dest='FILEPATH', default='.', help='source file path')
parser.add_argument('-n', '--name', dest='FILENAME', help='file name')

uploader_args = parser.parse_args()
