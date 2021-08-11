from hashlib import sha256
import copy

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

    def __str__(self):
        return '{0} {1} {2} {3} {4}'.format(self.address, self.nonce, self.balance, self.code, self.storage)

    def hash(self):
        return sha256(self.__str__()).hexdigest()

    def call_contract(self, storage):
        return eval(self.code, {storage: storage})

# The state of the entire world is just a set of Accounts
class WorldState:
    def __init__(self, accounts):
        self.accounts = accounts

    def __str__(self):
        return '\t'.join([account.__str__() for account in self.accounts.values()])

    def signature(self):
        return self.__str__()

class BlockChain:
    PRE_GENESIS_BLOCK_HASH = '00000000'
    def genesis_block(self):
        return Block([], self.PRE_GENESIS_BLOCK_HASH, self.genesis_world_state().signature())

    def genesis_world_state(self):
        # FIXME: deadbeef duplicated
        return WorldState({'0xdeadbeef': Account('0xdeadbeef', 0, 1000)})

    ## Toplevel BlockChain API
    def __init__(self):
        self.blocks = {self.genesis_block().hash(): self.genesis_block()}
        self.tx_queue = []

    def enqueue_transaction(self, tx):
        self.tx_queue.append(tx)

    def mine_new_block(self):
        # We first create a fake block. We just use it to calculate the end state signature.
        block_without_end_state_sig = Block(self.tx_queue, self.last_block().hash(), 'REPLACE_ME')
        sig = self.end_state_signature(block_without_end_state_sig)

        # Now that we have the end state sig, we commit the TXs, add the block to the chain, and empty the TX queue
        self.add_block(Block(self.tx_queue, self.last_block().hash(), sig))
        self.tx_queue = []


    def add_block(self, block):
        if not self.is_block_valid(block):
            print('New block is invalid')
            return

        self.blocks[block.hash()] = block

    def find_block_by(self, fun):
        return next(iter([b for b in self.blocks.values() if fun(b)]), None)

    def last_block(self):
        current_block = self.genesis_block()
        while True:
            next_block = self.find_block_by((lambda b: b.prev_block_hash == current_block.hash()))
            if next_block is None:
                break
            current_block = next_block
        return current_block


    ## Block methods
    def is_block_valid(self, block):
        if block.hash == self.genesis_block().hash():
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
        if block.hash() == self.genesis_block().hash():
            return self.genesis_world_state()

        state = self.end_state_for_block(self.blocks[block.prev_block_hash])
        for tx in block.transactions:
            state = self.apply_transaction(state, tx)
        return state

    def end_state_signature(self, block):
        return self.end_state_for_block(block).signature()

    ## Transaction Methods
    def apply_transaction(self, state, tx):
        # So apply_transaction doesn't mutate anything
        state = copy.deepcopy(state)

        sender_account = state.accounts[tx.sender_addr]
        if tx.nonce != sender_account.nonce:
            raise Exception('Transaction nonce must match that of sender account')

        # TODO: check well formed tx
        # TODO: do GAS calculations
        if tx.amount > sender_account.balance:
            raise Exception('{0} only has {1} balance. Not enough to cover {2} amount'.format(tx.sender_addr,
                sender_account.balance, tx.amount))

        # A None receiver_addr signals that this is a Contract Creation!
        if tx.receiver_addr is None:
            if tx.data is None:
                raise Exception('Contract creation must provide code via the data argument')
            contract_addr = sha256(tx.data)
            new_contract = Account(contract_addr, 0, 0, tx.data, {})
            state.accounts[new_contract.hash()] = new_contract
            return state

        # If we're trying to send ether to an account that doesn't exist yet, create it
        if tx.receiver_addr not in state.accounts:
            state.accounts[tx.receiver_addr] = Account(tx.receiver_addr, 0, 0, None, {})

        # Move the ether
        sender_account.balance -= tx.amount
        receiver_account = state.accounts[tx.receiver_addr]
        receiver_account.balance += tx.amount

        # Call the contract code if the receiver account is a Contract
        if receiver_account.type() == Account.CONTRACT:
            receiver_account.storage = receiver_account.call_contract(receiver_account.storage)
        return state


# Blocks contain multiple transactions
class Block:
    def __init__(self, transactions, prev_block_hash, end_state_signature):
        self.prev_block_hash = prev_block_hash
        self.transactions = transactions
        self.end_state_signature = end_state_signature

    def __str__(self):
        stringified_txs = '\t'.join([tx.__str__() for tx in self.transactions])
        return '{0}\t{1}\t{2}'.format(self.prev_block_hash, self.end_state_signature, stringified_txs)

    def hash(self):
        return sha256(self.__str__()).hexdigest()

# And each transaction changes the state S via APPLY(S, TX) => S'
class Transaction:
    def __init__(self, sender_addr, receiver_addr, amount, data):
        self.sender_addr = sender_addr
        self.receiver_addr = receiver_addr
        self.amount = amount
        self.data = data

    def __str__(self):
        return '{0},{1},{2},{3}'.format(self.sender_addr, self.receiver_addr, self.amount, self.data)


blockchain = BlockChain()
print('Accounts:')
print(blockchain.end_state_for_block(blockchain.last_block()))
