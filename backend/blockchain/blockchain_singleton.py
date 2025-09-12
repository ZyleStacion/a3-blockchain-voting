# Blockchain singleton instance
from blockchain.blockchain import Blockchain

blockchain = Blockchain()
from .blockchain import Blockchain

blockchain = Blockchain()
try:
    blockchain.load_chain()
except FileNotFoundError:
    pass
