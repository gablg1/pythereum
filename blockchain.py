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

    def to_string(self):
        return '{0} {1} {2} {3}'.format(self.nonce, self.balance, self.code, self.storage)

    def hash(self):
        return sha256(self.to_string()).hexdigest()



class BlockChain:
    GENESIS_BLOCK_HASH = '00000000'

    def __init__(self):
        self.accounts = {}
        self.blocks = {genesis_block().hash(): genesis_block()}

    def genesis_block(self):
        return Block([], GENESIS_BLOCK_HASH)

    def add_account(self, account):
        self.accounts[account.hash()] = account

    def add_block(self, block):
        if not block.is_valid(self.block_valid_from_hash):
            print('New block is invalid')
            return

        self.blocks[block.hash()] = block

    def block_valid_from_hash(self, block_hash):
        if block_hash == GENESIS_BLOCK_HASH:
            return True

        return block_hash in self.blocks and self.blocks[block_hash].is_valid()

    def end_state_from_block_hash(self, block_hash):
        if block_hash == GENESIS_BLOCK_HASH:
            return {}

        if block_hash not in self.blocks:
            raise Exception('Invalid block hash - not present')

        block = self.blocks[block_hash]
        state = self.end_state_from_block_hash(block.prev_block_hash)
        for tx in block.transactions:
            state = tx.apply(state)
        return state




class Block:
    def __init__(self, transactions, prev_block_hash):
        self.prev_block_hash = prev_block_hash
        self.transactions = transactions

    def prev_block(self, block_from_hash):


    def is_valid(self, block_valid_from_hash):
        if not block_valid_from_hash(self.prev_block_hash):
            return False

        # TODO: check timestamp

        # TODO: Check difficulty, block number, tx root

        # TODO: Check proof of work

        end_state_from_block_hash()



    
    def state_at_end_of_block(self):

    def to_string(self):
        stringified_txs = '\t'.join([tx.to_string() for tx in self.transactions])
        return '{0}\t{1}'.format(self.prev_block_hash, stringified_txs)

    def hash(self):
        return sha256(self.to_string()).hexdigest()

class Transaction:
    def __init__(self, ):
