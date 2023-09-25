from lib.client.common_args import create_common_args

parser = create_common_args('download', 'Download a file from a remote host')
parser.add_argument('-d', '--dst', dest='FILEPATH', default='.', help='destination file path')
parser.add_argument('-n', '--name', dest='FILENAME', help='file name')

downloader_args = parser.parse_args()
