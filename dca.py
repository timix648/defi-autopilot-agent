from wallet import w3, sign_and_send, get_agent_address
from config import AERODROME_ROUTER, TARGET_TOKEN, AERODROME_ABI, WETH_ADDRESS, ERC20_ABI
import time

def swap_eth_for_token(amount_eth):
    """Swap ETH for target token on Aerodrome"""
    agent_address = get_agent_address()
    if not agent_address:
        raise Exception("Agent address not set")
    
    contract = w3.eth.contract(address=AERODROME_ROUTER, abi=AERODROME_ABI)
    deadline = int(time.time()) + 300  # 5 minutes from now
    
    tx = contract.functions.swapExactETHForTokens(
        0, 
        [w3.to_checksum_address(WETH_ADDRESS), w3.to_checksum_address(TARGET_TOKEN)],
        agent_address,
        deadline
    ).build_transaction({
        'value': w3.to_wei(amount_eth, 'ether'),
        'from': agent_address,
        'gas': 300000
    })
    
    return sign_and_send(tx)

def swap_token_for_eth(amount_token):
    """Swap target token for ETH on Aerodrome"""
    agent_address = get_agent_address()
    if not agent_address:
        raise Exception("Agent address not set")
    
    contract = w3.eth.contract(address=AERODROME_ROUTER, abi=AERODROME_ABI)
    token_contract = w3.eth.contract(address=TARGET_TOKEN, abi=ERC20_ABI)
    approve_tx = token_contract.functions.approve(
        AERODROME_ROUTER,
        int(amount_token * (10 ** token_contract.functions.decimals().call()))
    ).build_transaction({
        'from': agent_address,
        'gas': 100000
    })
    sign_and_send(approve_tx)
    swap_tx = contract.functions.swapExactTokensForETH(
        int(amount_token * (10 ** token_contract.functions.decimals().call())),
        0, 
        [w3.to_checksum_address(TARGET_TOKEN), w3.to_checksum_address(WETH_ADDRESS)],
        agent_address,
        int(time.time()) + 300 
    ).build_transaction({
        'from': agent_address,
        'gas': 300000
    })
    
    return sign_and_send(swap_tx)