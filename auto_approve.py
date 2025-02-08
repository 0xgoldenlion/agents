from web3 import Web3
import time

# Web3 Configuration
RPC_URL = "https://sepolia.drpc.org"
CONTRACT_ADDRESS = "0x37B37f11c1Ad921739101849B357BA7ab7C8C592"
PRIVATE_KEY = "YourPrivateKey"
OWNER_ADDRESS = "0xYourOwnerWallet"


# Connect to blockchain
web3 = Web3(Web3.HTTPProvider(RPC_URL))
account = web3.eth.account.from_key(PRIVATE_KEY)


# Load contract ABI
contract_abi = '[{"inputs":[],"name":"requestLanding","outputs":[],"stateMutability":"nonpayable","type":"function"},' \
               '{"inputs":[{"internalType":"address","name":"drone","type":"address"}],"name":"getLandingStatus",' \
               '"outputs":[{"internalType":"bool","name":"","type":"bool"},{"internalType":"string","name":"","type":"string"}],' \
               '"stateMutability":"view","type":"function"},' \
               '{"inputs":[{"internalType":"address","name":"drone","type":"address"}],"name":"autoApproveLanding",' \
               '"outputs":[],"stateMutability":"nonpayable","type":"function"},' \
               '{"inputs":[],"name":"getAllRequests","outputs":[{"internalType":"tuple[]","name":"","type":"tuple[]","components":[' \
               '{"internalType":"address","name":"drone","type":"address"},' \
               '{"internalType":"bool","name":"approved","type":"bool"},' \
               '{"internalType":"string","name":"landingZone","type":"string"}]}],' \
               '"stateMutability":"view","type":"function"}]'


contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

def auto_approve_requests():
    """ AI agent that monitors requests and auto-approves landings """
    print("AI Agent started: Monitoring landing requests...")
    
    while True:
        try:
            # Get all requests from contract
            requests = contract.functions.getAllRequests().call()

            for request in requests:
                drone = request[0]  # Extract drone address
                approved = request[1]  # Extract approval status
                
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
                    
                    print(f"Landing approved on-chain: {tx_hash.hex()}")
                    time.sleep(10)  # Pause after sending transaction
            
        except Exception as e:
            print(f"Error: {e}")  # Prevents exit on failure
        
        time.sleep(5)  # Check every 5 seconds


if __name__ == "__main__":
    auto_approve_requests()