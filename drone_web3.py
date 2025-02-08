from web3 import Web3
import time

# Web3 Configuration
RPC_URL = "https://sepolia.drpc.org" #sepolia
CONTRACT_ADDRESS = "0xEed75413d7E0142d032d403110177FaE42790166"
PRIVATE_KEY = "YourPrivateKey"  
DRONE_ADDRESS = "0xYourDroneWallet"

# Connect to blockchain
web3 = Web3(Web3.HTTPProvider(RPC_URL))
account = web3.eth.account.from_key(PRIVATE_KEY)

# Load contract ABI
contract_abi = '[{"inputs":[],"name":"requestLanding","outputs":[],"stateMutability":"nonpayable","type":"function"},' \
               '{"inputs":[{"internalType":"address","name":"drone","type":"address"},{"internalType":"string","name":"zone","type":"string"}],' \
               '"name":"approveLanding","outputs":[],"stateMutability":"nonpayable","type":"function"},' \
               '{"inputs":[{"internalType":"address","name":"drone","type":"address"}],"name":"getLandingStatus",' \
               '"outputs":[{"internalType":"bool","name":"","type":"bool"},{"internalType":"string","name":"","type":"string"}],' \
               '"stateMutability":"view","type":"function"}]'

contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)


def request_landing():
    """ Sends a landing request to the smart contract. """
    print("Requesting landing permission on blockchain...")
    tx = contract.functions.requestLanding().build_transaction({
    'from': DRONE_ADDRESS,
    'gas': 900000,
    'maxFeePerGas': web3.to_wei(100, 'gwei'),  # Setting max fee per gas to 2 Gwei
    'maxPriorityFeePerGas': web3.to_wei(100, 'gwei'),  # Setting max priority fee per gas to 1 Gwei
    'nonce': web3.eth.get_transaction_count(DRONE_ADDRESS)
})
    signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"Transaction sent: {tx_hash.hex()}")
    return tx_hash.hex()


def wait_for_landing_approval():
    """ Waits until landing is approved and returns the landing zone. """
    print("Waiting for landing approval...")
    while True:
        approved, landing_zone = contract.functions.getLandingStatus(DRONE_ADDRESS).call()
        if approved:
            print(f"Landing Approved! Assigned landing zone: {landing_zone}")
            return landing_zone
        time.sleep(5)  # Check every 5 seconds
