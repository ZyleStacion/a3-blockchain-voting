import datetime
import hashlib
import json

class Block:
    def __init__(self, block_index, time_created, transactions, previous_hash, nonce):
        """_summary_

        Args:
            block_index (_type_):  Index of the block
            time_created (_type_): Timestamp of block create
            transactions (_type_): Lists of transactions
            previous_hash (_type_): Hash value from the previous blockj
            nonce (_type_): The proof-of-work nonce that produced a valid block hash.
        """
        self.block_index = block_index
        self.time_created = time_created 
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.hash = self.hash_block()
        self.nonce = nonce

    def to_dict(self) -> dict:
        """
        Return a serialize dictionary of block object
        """
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "proof": self.proof,
            "previous_hash": self.previous_hash,
        }
    
class Transactions:
    def __init__(self, transaction_id, sender, receiver, amount):
        """
        Initialize new tranasctions

        Args:
            transaction_id (_type_): Unique ID for transactions
            sender (_type_):  The user or system creating/sending the transaction.
            receiver (_type_): User receviing the transactions
            amount (_type_): Amount sent
        """
        self.ids = transaction_id
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
    
    def to_dict(self):
        """
        Return a serializable dictionary of Transaction

        """
        return {
            "id": self.ids,
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
        }    

class Blockchain: 
    # This class will store data which a normal blockchain should have
    def __init__(self):

        self.chain = []
        self.pending_transactions = []
        self.difficulty =3 # Default difficulty
        
        # Populate the block
        genesis_txs = [
            {"id": "tx000", "sender": "ADMIN", "receiver": "Alice", "amount": 1000},
            {"id": "tx0001", "sender": "ADMIN", "receiver": "Jeff", "amount": 1000},
            {"id": "tx0002", "sender": "ADMIN", "receiver": "Carl", "amount": 1000},
            {"id": "tx0003", "sender": "ADMIN", "receiver": "Edward", "amount": 1000},
            {"id": "tx0004", "sender": "ADMIN", "receiver": "Kate", "amount": 1000},
            {"id": "tx0005", "sender": "ADMIN", "receiver": "Joe", "amount": 1000},
            {"id": "tx0006", "sender": "ADMIN", "receiver": "John", "amount": 1000},
        ]
        # In a real block chain, the sender, and receiver will be a form of the wallet address not name
        self.create_block(
            data="Genesis Block",
            proof=1,
            previous_hash="0",
            index=0,
        )
        
        # Store genesis transactions inside the first block
        self.chain[0]["transactions"] = genesis_txs

    def to_digest(self, new_proof: int, previous_proof: int, index: str, data: str) -> bytes:
        """
        Its job is to hashed the inputted string and it will results
        in unique string of bytes -> for miner to solve

        Args:
            new_proof (int): new proof from the new block
            previous_proof (int): Proof from previous block
            index (str): Index of a block
            data (str): The data of the block

        Returns:
            bytes: Hashed value of inputted string
        """
        #
        
        to_digest = str(new_proof ** 2 - previous_proof **2 + index) + data
        return to_digest.encode()
    
    # Proof of work
    def proof_of_work(self, previous_proof: int, index: int, data: str) -> int:
        """
        Perform the Proof-of-Work (PoW) algorithm to find a valid proof (nonce) 
        for the next block in the blockchain.

        The function repeatedly tests different values of `new_proof` until it 
        finds one that produces a SHA-256 hash with the required number of leading 
        zeros (difficulty target). This ensures that miners must expend 
        computational effort to create a valid block, securing the blockchain 
        against tampering.

        Args:
            previous_proof (int):Proof from previous block
            index (int): Index of a block
            data (str): The data of the block

        Returns:
            int: The valid proof (nonce) that satisfies the difficulty condition.
        """
        
        new_proof = 1
        while True:
            # Generate candidate hash
            to_digest = self.to_digest(new_proof, previous_proof, index, data)
            hash_value = hashlib.sha256(to_digest).hexdigest()

            # Show every nonce attempt
            print(f"Nonce: {new_proof} -> Hash: {hash_value}") # Print all the nonce value till it finds correct nonce

            # Stop if hash meets difficulty requirement
            if hash_value.startswith("0" * self.difficulty):
                print(f"Valid nonce found: {new_proof} with hash {hash_value}")
                return new_proof
            
            # Increment nonce
            new_proof += 1
    
    #Adjust difficulty of mining
    def difficulty_adjustment(self):
        old_difficulty = self.difficulty
        
        if len(self.chain) %  5 ==0:
            self.difficulty += 1
        elif self.difficulty > 1 and len(self.chain) & 7 == 0:
            self.difficulty -= 1
            
        if self.difficulty != old_difficulty:
            print(f"Difficulty adjusted: {old_difficulty} -> {self.difficulty}")
        else:
            print(f"Difficulty remains at: {self.difficulty}")
    
    # Hash value
    def hash_value(self, block):
        """
        Hash block using SHA-256

        Args:
            block (_type_): Block that is used tobe hashed

        Returns:
            _type_:  The SHA-256 value of the hashed blocked
        """
        block_copy = dict(block)
        block_copy.pop("hash", None)

        encoded_block = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
              
    # ---- Block ----
    def mine_block(self, data: str, miner: str) -> dict: 
        """
        Mine a new block and add it into the blockchain.

        Args:
            data (str): Data to include in the block
            miner (str): User that mine the block

        Returns:
            dict: Dictionary of the created block
            
        - Proof-of-Work is a probabilistic process and may require 
          thousands or millions of attempts before a valid proof 
          is found.
        - A mining reward transaction is automatically created and 
          assigned to the miner.
        - Pending transactions are cleared after being added to 
          the block.
          
        """
        print(f"Current difficulty {self.difficulty}...")
        
        #Get previous block
        previous_block = self.get_previous_block()
        previous_proof = previous_block["proof"]
        index = previous_block["index"] + 1
        
        #Find valid proof
        proof = self.proof_of_work(previous_proof, index, data)
        
        #When proof is found reward user 
        reward_tx = {
            "id": f"reward_{len(self.chain)+1}",  # unique reward ID
            "sender": "SYSTEM",
            "receiver": miner,
            "amount": 10,  # reward amount
        }
        self.pending_transactions.append(reward_tx)

        #Link preivous hash
        previous_hash = self.hash_value(previous_block)

        # Create the new block with reward + all pending transactions
        block = self.create_block(
            data=data,
            proof=proof,
            previous_hash=previous_hash,
            index=index
        )
        
        # Adjust difficulty
        self.difficulty_adjustment()

        print(f"Block mined at difficulty {self.difficulty}. Nonce: {proof}, Hash: {block['hash']}")
        return block
    
    # Create block
    def create_block(self, data: str, proof: int, previous_hash: str, index: int) -> dict:
        """Create a block within the blockchain

        Args:
            data (str): Data that is included in the block
            proof (int): The valid proof found when mining
            previous_hash (str): Hash value of the previous block
            index (int): Index of a block 

        Returns:
            dict: Dictionary of the newly created block
        """
        block = {
            "index": index,
            "timestamp": str(datetime.datetime.now()),
            "data": data,
            "transactions": self.pending_transactions.copy(),   # include txs here
            "proof": proof,
            "previous_hash": previous_hash,
            "difficulty": self.difficulty,
            "none": proof
        }
        block["hash"] = self.hash_value(block)
        self.pending_transactions = []  # clear the pool after mining
        self.chain.append(block)
        return block
    
    # Get previous block
    def get_previous_block(self) -> dict:
        """
        Return the dictionary of a previous block

        Returns:
            dict: Dictionary of the previous block
        """
        return self.chain[-1] 
    
    # Chain integreity 
    def is_chain_valid(self) -> bool:
        """
        Ensure that the chain is still valid and no alteration has been made.
        """
        previous_block = self.chain[0]
        block_index = 1

        while block_index < len(self.chain):
            block = self.chain[block_index]

            if block['previous_hash'] != self.hash_value(previous_block):
                return False

            current_proof = previous_block['proof']
            next_index, next_data, next_proof = (
                block["index"],
                block["data"],
                block["proof"],
            )


            hash_value = hashlib.sha256(self.to_digest(
                new_proof=next_proof,
                previous_proof=current_proof,
                index=next_index,
                data=next_data
            )).hexdigest()

            if not hash_value.startswith("0" * block["difficulty"]):
                return False

            previous_block = block
            block_index += 1

        return True

              
    # ---- DATA PERSISTENCE ----
    # Save Blockchain
    def save_chain(self):
        """
        Save chain in a form of json file when newly blocks has been added into the chain.
        """
        with open("blockchain.json", "w") as f:
            json.dump(self.chain, f , indent=4)

    # Load block chain
    def load_chain(self):
        """
        Load chain from json file
        """
        with open("blockchain.json", "r") as f:
             self.chain = json.load(f)

    # ---- TRANSACTIONS ----
    def get_balance(self, user: str) -> float:
        """
        A helper functions to get user's balance

        Args:
            user (str): Input user name
        Returns:
            float: Return the balance number of in
        """
        balance = 0.0

        # Confirmed transactions
        for block in self.chain:
            for tx in block["transactions"]:
                sender = tx.get("sender")
                receiver = tx.get("receiver")
                amount = tx.get("amount", 0)  

                if sender == user:
                    balance -= amount
                if receiver == user:
                    balance += amount

        # Pending transactions
        for tx in self.pending_transactions:
            sender = tx.get("sender")
            receiver = tx.get("receiver")
            amount = tx.get("amount", 0)

            if sender == user:
                balance -= amount
            if receiver == user:
                balance += amount

        return balance

    #Check transactions
    def check_transactions(self, tx_id: str) -> bool: # 
        """
        Check for duplication transactions_id so that only 1 transactions id can exists
        Used to prevent double spending 

        Args:
            tx_id (str): Inputted transactions to check

        Returns:
            bool: If transactions id exists true, else if not exist yet false.
        """
        if not tx_id:
            return False # No tx exists
        
        for transactions in self.pending_transactions:
            if transactions.get("id") == tx_id:
                return True
        for block in self.chain:
            for transactions in block.get("transactions", []):
                if transactions.get("id") == tx_id:
                    return True
        return False
    
    def exists_transactions(self, tx_id: str) -> bool:
        """
        Check for exists transactions in block or pending transactions

        Args:
            tx_id (str): Transactions Id to check

        Returns:
            bool: Return True if transactions exists, else return Falase if don't exists
        """
        return self.check_transactions(tx_id)

    #Insert Transactions
    def insert_transaction(self, transaction: Transactions) -> bool: 
        """
        Insert transactions new transactions. 
        The newly inserted transactions won't be confirmed yet.
        It will only be confired when someone successfully mined a block.
        
        Returns:
            _type_: True if insert transactions succesfully, if fail to insert false
        """
        if not isinstance(transaction, Transactions):
            return False

        tx = transaction.to_dict()

        if not self.validate_transaction(tx):
            return False

        if self.exists_transactions(tx["id"]):
            return False

        self.pending_transactions.append(tx)

        return True

    #Validate transactions
    def validate_transaction(self, tx: dict) -> bool:
        """
        Validate transaction before adding

        Args:
            tx (dict): Dictionary format of the transaction

        Returns:
            bool: Return true if transaction is valid, if not false.
        """
        sender = tx.get("sender")
        receiver = tx.get("receiver")
        amount = tx.get("amount")

        if not sender or not receiver or amount is None:
            return False

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return False

        if amount < 0:
            return False

        if sender != "SYSTEM":  # Allow mining rewards or system tx
            balance = self.get_balance(sender)
            if amount > balance:
                return False

        return True