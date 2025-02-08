from web3 import Web3
import time

# Web3 Configuration
RPC_URL = "https://your_rpc_url"
CONTRACT_ADDRESS = "0xYourContractAddress"
PRIVATE_KEY = "YourPrivateKey"
OWNER_ADDRESS = "0xYourOwnerWallet"


# Connect to blockchain
web3 = Web3(Web3.HTTPProvider(RPC_URL))
account = web3.eth.account.from_key(PRIVATE_KEY)

# Load contract ABI
contract_abi = '[{"inputs":[],"name":"requestLanding","outputs":[],"stateMutability":"nonpayable","type":"function"},' \
               '{"inputs":[{"internalType":"address","name":"drone","type":"address"}],"name":"autoApproveLanding",' \
               '"outputs":[],"stateMutability":"nonpayable","type":"function"},' \
               '{"inputs":[{"internalType":"address","name":"drone","type":"address"}],"name":"getLandingStatus",' \
               '"outputs":[{"internalType":"bool","name":"","type":"bool"},{"internalType":"string","name":"","type":"string"}],' \
               '"stateMutability":"view","type":"function"}]'

contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

def auto_approve_requests():
    """ AI agent that monitors requests and auto-approves landings """
    print("AI Agent started: Monitoring landing requests...")
    while True:
        # Simulate AI decision by checking the smart contract
        for drone in [OWNER_ADDRESS]:  # Replace with a list of drones to monitor
            approved, _ = contract.functions.getLandingStatus(drone).call()
            if not approved:
                print(f"Auto-approving landing for {drone}...")
                tx = contract.functions.autoApproveLanding(drone).build_transaction({
                    'from': OWNER_ADDRESS,
                    'gas': 900000,
                    'maxFeePerGas': web3.to_wei(100, 'gwei'),  
                    'maxPriorityFeePerGas': web3.to_wei(100, 'gwei'),  
                    'nonce': web3.eth.get_transaction_count(OWNER_ADDRESS)
                })
                signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
                tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                time.sleep(10)
                print(f"Landing approved on-chain: {tx_hash.hex()}")
        
        time.sleep(5)  # Check every 5 seconds

if __name__ == "__main__":
    auto_approve_requests()
