# pythereum
A simple and didactic implementation of Ethereum in 200 lines of Python code, following the
model described in the original [Ethereum white paper](https://ethereum.org/en/whitepaper/).

# Running it
Run it with `python blockchain.py`. The blockchain starts with the genesis block and a single `deadbeef` account containing 1000 ether.

```
Account: deadbeef
Nonce: 0, Balance: 1000
Code: None
Storage: {}
```

# Send ether between accounts
Submit transactions by typing up `from_addr to_addr nonce amount 'data'` in the prompt. 
Try sending 50 ether to a newly created account with address `hellokit` via the following transaction:
```
deadbeef hellokit 0 50 None
```

The third argument is a nonce: a variable that ensures the same transaction doesn't get sent twice.
Each account has a nonce that starts at 0 and increments every time the account sends a transaction.
The transaction nonce must always match the nonce of the account sending the transaction.

# Create a contract
Now to the fun part! Create a new contract by submitting a transaction to the `None` address

```
deadbeef None 1 0 'storage["foo"] = args["my_arg"]'
```
The last argument `'storage["foo"] = args["my_arg"]'` is the actual code for the contract. Instead of Solidity and the EVM, our implementation accepts regular Python code!

Under the hood our contract is just an Ethereum Account containing the above code and an initially empty storage. This particular contract got stored at address `9b241ab9`.

# Calling your contract
To call your newly created contract just submit a 0 ether transaction to the contract's addresss:
```
deadbeef 9b241ab9 2 0 '{"my_arg": 42}'
```

Now the world state should be
```
Account: hellokit
Nonce: 0, Balance: 50
Code: None
Storage: {}

Account: deadbeef
Nonce: 3, Balance: 950
Code: None
Storage: {}

Contract Account: 9b241ab9
Nonce: 0, Balance: 0
Code: storage["foo"] = args["my_arg"]
Storage: {'foo': 42}
```

And notice that our contract now has `{'foo': 42}` in its storage because we called it passing args `{"my_arg": 42}`!

# Parallel with real Ethereum
The interface of `pythereum` is similar in spirit to the interface that dApp clients use to talk with real Ethereum nodes. Here you type a transaction on the prompt, but, in a real dApp, the frontend code would connect with a node in the Ethereum network and submit a transaction very much like the ones above in order to call a smart contract.

This implementation has many simplifications:
- It's not distributed (you're just running a single pythereum node when you run `python blockchain.py`)
- We don't handle Gas and security concerns of executing arbitrary user code
- We don't implement any real notion of mining / proof of work / proof of stake

But hopefully it can be used as a starting point for people to understand Ethereum and Blockchain better!
