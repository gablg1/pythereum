from hashlib import sha256

# The state of Ethereum is the set of all accounts
class Account:
    EXTERNALLY_OWNED = 'externally_owned'
    CONTRACT = 'contract'

    def __init__(self, address, nonce, balance, code=None, storage={}):
        self.address = address
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
    def genesis_block(self):
        return Block([], GENESIS_BLOCK_HASH)

    ## Toplevel BlockChain API
    def __init__(self):
        self.accounts = {}
        self.blocks = {genesis_block().hash(): genesis_block()}
        self.tx_queue = []

    def find_or_create_empty_account(self, address):
        if account_hash not in self.accounts:
            self.accounts[address] = Account(address, 0, 0, None, {})
        return self.accounts[address]

    def add_block(self, block):
        if not self.is_block_valid(block):
            print('New block is invalid')
            return

        self.blocks[block.hash()] = block

    def find_block_by(self, fun):
        return next(iter([b for b in self.blocks.values() if fun(b)]), None)

    def last_block(self):
        current_block = genesis_block()
        while (next_block = self.find_block_by(lambda b: b.prev_block_hash == next_block.hash())) is not None:
            current_block = next_block
        return current_block

    def enqueue_transaction(self, tx):
        self.tx_queue.append(tx)

    def mine_new_block(self):

    ## Block methods
    def is_block_valid(self, block):
        if block.hash == GENESIS_BLOCK_HASH:
            return True

        # Check that the previous block is valid
        if (block.prev_block_hash not in self.blocks or
                not self.is_block_valid(self.blocks[block.prev_block_hash])):
            return False

        # TODO: check timestamp

        # TODO: Check difficulty, block number, tx root

        # TODO: Check proof of work

        return self.end_state_signature(block) == block.end_state_signature

    def end_state_for_block(self, block):
        if block.hash == GENESIS_BLOCK_HASH:
            return {}

        state = self.end_state_for_block(self.blocks[block.prev_block_hash])
        for tx in block.transactions:
            state = self.apply_transaction(state, tx)
        return state

    def signature_of_block_state(self, state):
        return sha256('{0}'.format(state)).hexdigest()

    def end_state_signature(self, block):
        return self.signature_of_block_state(self.end_state_for_block(block))

    ## Transaction Methods
    def apply_transaction(self, state, tx):
        if tx.nonce != (sender_account = self.accounts[tx.sender_addr]).nonce:
            raise Exception('Transaction nonce must match that of sender account')

        # TODO: check well formed tx
        # TODO: do GAS calculations
        if tx.amount > sender_account.balance:
            raise Exception('{0} only has {1} balance. Not enough to cover {2} amount'.format(tx.sender_addr,
                sender_account.balance, tx.amount))

        # Move money, creating the receiver account if necessary
        sender_account.balance -= tx.amount
        receiver_account = self.find_or_create_empty_account(tx.receiver_addr)
        receiver_account.balance += tx.amount

        if receiver_account.type() == Account.CONTRACT:
            receiver_account.

    ## Account Methods
    def call_contract(self, account):
        def send_message(receiver_addr, amount, data):

        return eval(account.code, {storage: account.storage, send_message: self.send_message})

    def send_message(self, receiver_addr, amount, data):


# Blocks contain multiple transactions
class Block:
    def __init__(self, transactions, prev_block_hash, end_state_signature):
        self.prev_block_hash = prev_block_hash
        self.transactions = transactions
        self.end_state_signature = end_state_signature

    def to_string(self):
        stringified_txs = '\t'.join([tx.to_string() for tx in self.transactions])
        return '{0}\t{1}'.format(self.prev_block_hash, stringified_txs)

    def hash(self):
        return sha256(self.to_string()).hexdigest()

# And each transaction changes the state S via APPLY(S, TX) => S'
class Transaction:
    def __init__(self, sender_addr, receiver_addr, amount):
        self.sender_addr = sender_addr
        self.receiver_addr = receiver_addr
        self.amount = amount
