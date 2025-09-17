import datetime
import hashlib
import json

class Block:
    def __init__(self, block_index, time_created, transactions, previous_hash, nonce):
    
        self.block_index = block_index
        self.time_created = time_created 
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.hash = self.hash_block()
        self.nonce = nonce

    def to_dict(self) -> dict:
        return {
            "index": self.block_index,
            "timestamp": self.time_created,
            "transactions": self.transactions,
            "nonce": self.nonce,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }


class Transactions:
    def __init__(self, transaction_id, sender, charity_receive, ticket_sent):
        self.ids = transaction_id
        self.sender = sender
        self.charity_receive = charity_receive
        self.ticket_sent = ticket_sent
    
    def to_dict(self):
        return {
            "id": self.ids,
            "sender": self.sender,
            "charity_receive": self.charity_receive,
            "ticket_sent": self.ticket_sent,
        }    

class Blockchain: 
    # This class will store data which a normal blockchain should have
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.difficulty = 3

        genesis_txs = [
            {
                "id": "genesis_tx_0",
                "sender": "SYSTEM",
                "charity_receive": "DAO_POOL",
                "ticket_sent": 0,
                "description": "Genesis block for DAO voting and donation system"
            }
        ]

        genesis_block = {
            "index": 0,
            "timestamp": str(datetime.datetime.utcnow()),
            "data": "Genesis Block",
            "transactions": genesis_txs,
            "proof": 1,  # could also run proof_of_work
            "previous_hash": "0",
            "difficulty": self.difficulty,
        }
        genesis_block["hash"] = self.hash_value(genesis_block, include_hash=False)
        self.chain.append(genesis_block)


    def to_digest(self, new_proof: int, previous_proof: int, index: int, data: str, transactions: list = None) -> bytes:
        if transactions is None:
            transactions = []
        tx_string = json.dumps(transactions, sort_keys=True)
        to_digest = f"{new_proof}{previous_proof}{index}{data}{tx_string}".encode()
        return to_digest

        # Proof of work
    def proof_of_work(self, previous_proof: int, index: int, data: str, transactions: list = None) -> int:
        """
        Simplified Proof-of-Work for DAO voting.
        Ensures tamper resistance without requiring heavy mining.
        """
        if transactions is None:
            transactions = []

        new_proof = 1
        while True:
            # Include transactions so votes matter in PoW
            tx_string = json.dumps(transactions, sort_keys=True)
            to_digest = f"{new_proof}{previous_proof}{index}{data}{tx_string}".encode()

            hash_value = hashlib.sha256(to_digest).hexdigest()

            if hash_value.startswith("0" * self.difficulty):
                return new_proof

            new_proof += 1

    #Adjust difficulty of mining
    def difficulty_adjustment(self):
        old_difficulty = self.difficulty
        
        if len(self.chain) %  5 ==0:
            self.difficulty += 1
        elif self.difficulty > 1 and len(self.chain) & 7 == 0:
            self.difficulty -= 1
            
    # Hash value
    def hash_value(self, block: dict, include_hash: bool = False) -> str:
        block_copy = dict(block)
        if "hash" in block_copy and not include_hash:
            block_copy.pop("hash")
        encoded_block = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()


    # ---- Block ----
    def auto_mine_block(self, data: str = "Vote Block") -> dict:
        if not self.pending_transactions:
            return None

        previous_block = self.get_previous_block()
        previous_proof = previous_block["proof"]
        index = previous_block["index"] + 1

        proof = self.proof_of_work(previous_proof, index, data)
        previous_hash = self.hash_value(previous_block)

        block = self.create_block(
            data=data,
            proof=proof,
            previous_hash=previous_hash,
            index=index
        )

        self.difficulty_adjustment()

        # 🟢 Save chain every time a block is mined
        self.save_chain()

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
            "transactions": self.pending_transactions.copy(),
            "proof": proof,
            "previous_hash": previous_hash,
            "difficulty": self.difficulty,
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
        Ensure the chain is valid:
        - Each block correctly references the previous hash
        - Each block's proof-of-work is valid
        - Each block's stored hash matches its actual contents
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # 1. Check previous_hash link (ignore 'hash' field in computation)
            if current_block["previous_hash"] != self.hash_value(previous_block, include_hash=False):
                return False

            # 2. Validate proof-of-work
            proof = current_block["proof"]
            prev_proof = previous_block["proof"]
            index = current_block["index"]
            data = current_block["data"]

            check_hash = hashlib.sha256(
                self.to_digest(
                    new_proof=proof,
                    previous_proof=prev_proof,
                    index=index,
                    data=data,
                )
            ).hexdigest()

            if not check_hash.startswith("0" * current_block["difficulty"]):
                return False

            # 3. Ensure stored hash matches actual block hash
            if current_block.get("hash") != self.hash_value(current_block, include_hash=False):
                return False

        return True

              
    # ---- DATA PERSISTENCE ----
    # Save Blockchain
    def save_chain(self):
        def convert_bytes(obj):
            if isinstance(obj, bytes):
                return obj.decode()  # or use base64 if it's binary content
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

        with open("blockchain.json", "w") as f:
            json.dump(self.chain, f, indent=4, default=convert_bytes)

    # Load block chain
    def load_chain(self):
        """
        Load chain from json file
        """
        with open("blockchain.json", "r") as f:
             self.chain = json.load(f)

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
        sender = tx.get("sender")
        charity_receive = tx.get("charity_receive")
        ticket_sent = tx.get("ticket_sent")

        if not sender or charity_receive is None or ticket_sent is None:
            return False

        try:
            ticket_sent = int(ticket_sent)
        except (TypeError, ValueError):
            return False

        if ticket_sent < 0:
            return False

        # Ensure charity_receive is string before checks
        charity_str = str(charity_receive)

        # Special case: votes (proposal IDs allowed)
        if charity_str.startswith("proposal_") or charity_str.isdigit():
            return True

        # Normal donation/payment logic
        if sender != "SYSTEM" and charity_str != "DAO_POOL":
            balance = self.get_balance(sender)
            if ticket_sent > balance:
                return False

        return True
