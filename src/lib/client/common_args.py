import argparse


def create_common_args(prog: str, description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog,
        description=description)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='increase output verbosity'
    )
    group.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help='decrease output verbosity'
    )
    parser.add_argument(
        '-H',
        '--host',
        dest='ADDR',
        type=str,
        default='localhost',
        help='server IP address'
    )
    parser.add_argument(
        '-p',
        '--port',
        dest='PORT',
        type=int,
        default=8082,
        help='server port'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-sw',
        '--stop_and_wait',
        action='store_true',
        help='stop and wait protocol'
    )
    group.add_argument(
        '-sr',
        '--selective_repeat',
        action='store_true',
        help='selective repeat protocol'
    )
    return parser
