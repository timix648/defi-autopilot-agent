import logging

from config import EXTRA_POOL, TARGET_TOKEN, ERC20_ABI, EXTRA_ABI
from wallet import sign_and_send, get_agent_address,w3

def stake_token(amount):
    """Stake tokens on Extra Finance"""
    agent_address = get_agent_address()  # Get agent address here
    if not agent_address:
        raise Exception("Agent address not set")
    
    try:
        token_contract = w3.eth.contract(address=TARGET_TOKEN, abi=ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_wei = int(amount * (10 ** decimals))
        
        # Approve spending
        approve_tx = token_contract.functions.approve(
            EXTRA_POOL, 
            amount_wei
        ).build_transaction({
            'from': agent_address  # Use agent_address
        })
        sign_and_send(approve_tx)
        
        # Deposit to pool
        pool_contract = w3.eth.contract(address=EXTRA_POOL, abi=EXTRA_ABI)
        deposit_tx = pool_contract.functions.deposit(
            TARGET_TOKEN,
            amount_wei
        ).build_transaction({
            'from': agent_address  # Use agent_address
        })
        
        return sign_and_send(deposit_tx)
    except Exception as e:
        logging.exception(f"❌ Staking failed")
        return None

def unstake_token(amount):
    """Unstake tokens from Extra Finance"""
    agent_address = get_agent_address()  # Get agent address here
    if not agent_address:
        raise Exception("Agent address not set")
    try:
        pool_contract = w3.eth.contract(address=EXTRA_POOL, abi=EXTRA_ABI)
        unstake_tx = pool_contract.functions.withdraw(
            TARGET_TOKEN,
            int(amount * (10 ** 6))  # USDbC uses 6 decimals
        ).build_transaction({
            'from': agent_address  # Use agent_address
        })
        return sign_and_send(unstake_tx)
    except Exception as e:
        logging.exception(f"❌ Unstaking failed")
        return None