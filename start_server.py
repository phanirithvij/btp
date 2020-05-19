import argparse
import os

from server import run_app, app

parser = argparse.ArgumentParser(description='SPKID and LID demo')
parser.add_argument(
    '--progs',
    choices=['lid', 'spkid'],
    nargs='+', default=['lid', 'spkid'],
    help='Pass the required demo programs (default: lid spkid)',
)
parser.add_argument(
    '-d', '--dir',
    default='./data',
    help='Main Directory which the server uses as storage (default: ./data)',
)
parser.add_argument(
    '-p', '--port',
    type=int, default=3000,
    help='Flask port (default: 3000)',
)


args = parser.parse_args()
dirname = os.path.abspath(args.dir)

# create the dir
try:
    os.makedirs(dirname)
except FileExistsError:
    pass
except Exception as e:
    print(e)

if not os.access(args.dir, os.R_OK):
    raise argparse.ArgumentTypeError(f"No such directory {dirname}")

# print(args)

app.config['UPLOAD_FOLDER'] = dirname
app.debug = True
run_app(host='0.0.0.0', port=3000, debug=True)
