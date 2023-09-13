import argparse

parser = argparse.ArgumentParser(
                prog='start-server',
                description='Start server')

group = parser.add_mutually_exclusive_group(required=False)
group.add_argument('-v', '--verbose', action='store_false', help='increase output verbosity')
group.add_argument('-q', '--quiet', action='store_true', help='decrease output verbosity')  
parser.add_argument('-H', '--host', dest='ADDR', help='service IP address')
parser.add_argument('-p', '--port', dest='PORT', type=int, default=80, help='service port')
parser.add_argument('-s', '--storage', dest='DIRPATH', default='.', help='storage dir path')

server_args = parser.parse_args()
