from config.debug_messages import debug_messages
from config.known_addresses import KNOWN_ADDRESSES
from config.known_solutions import KNOWN_SOLUTIONS

import os
import sys

# Update data directory path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Add lib directory to Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, 'lib')
sys.path.insert(0, LIB_DIR)

# Update import statement
from lib.cryptos.ripemd160 import hash160

# Update data directory path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data') 