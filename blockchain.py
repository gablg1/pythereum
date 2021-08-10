import sha256 from hashlib

class Account:
    EXTERNALLY_OWNED = 'externally_owned'
    CONTRACT = 'contract'

    def __init__(self, nonce, balance, code=None, storage={}):
        self.nonce = nonce
        self.balance = balance
        self.code = code
        self.storage = storage

    def type(self):
        return EXTERNALLY_OWNED if self.code is None else CONTRACT


class BlockChain:
    def __init__(self):
        self.accounts = {}
        self.blocks = [genesis_block()]

    def genesis_block(self):
        return Block([], '00000000')

class Block:
    def __init__(self, transactions, prev_block_hash):
        self.prev_block_hash = prev_block_hash
        self.transactions = transactions

    def to_string(self):
        ret = ''
        for tx in self.transactions:
            ret += tx.to_string()
        return '{0}\t{1}'.format(self.prev_block_hash, ret)

    def hash(self):
        return sha256(self.to_string()).hexdigest()

class Transaction:
    def __init__(self, ):
