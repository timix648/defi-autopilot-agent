from web3 import Web3
from config import TARGET_TOKEN, ERC20_ABI, BASE_RPC_URL
import os

w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))

def save_agent_address(address):
    with open('.agent_address', 'w') as f:
        f.write(address)

def get_agent_address():
    try:
        with open('.agent_address', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def get_eth_balance():
    address = get_agent_address()
    if not address:
        return 0.0
    balance_wei = w3.eth.get_balance(address)
    return w3.from_wei(balance_wei, 'ether')

def sign_and_send(transaction_dict):
    """Simulated transaction signing for demo purposes"""
    if not get_agent_address():
        raise Exception("No wallet connected")
    return {
        'tx_hash': Web3.keccak(text=f"demo_tx_{int(time.time())}").hex()
    }

def get_token_balance():
    address = get_agent_address()
    if not address:
        return 0.0
        
    try:
        token_contract = w3.eth.contract(
            address=TARGET_TOKEN,
            abi=ERC20_ABI
        )
        decimals = token_contract.functions.decimals().call()
        balance = token_contract.functions.balanceOf(address).call()
        return balance / (10 ** decimals)
    except Exception as e:
        print(f"Token balance error: {str(e)}")
        return 0.0