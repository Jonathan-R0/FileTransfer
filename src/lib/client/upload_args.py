from src.lib.client.common_args import create_common_args

parser = create_common_args('upload', 'Send a file to a remote host')
parser.add_argument('-s', '--src', dest='FILEPATH', default='.', help='source file path')
parser.add_argument('-n', '--name', dest='FILENAME', help='file name')

uploader_args = parser.parse_args()
