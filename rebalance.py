import logging
from wallet import get_eth_balance, get_token_balance, w3, sign_and_send
from config import ETH_USD_FEED, REBALANCE_THRESHOLD, CHAINLINK_ABI
from dca import swap_eth_for_token, swap_token_for_eth
from dca import swap_token_for_eth
import requests

def get_eth_price():
    """Robust ETH price fetching with fallbacks"""
    try:
       checksum_address = w3.to_checksum_address(ETH_USD_FEED)
       contract = w3.eth.contract(address=checksum_address, abi=CHAINLINK_ABI)
       contract = w3.eth.contract(address=ETH_USD_FEED, abi=CHAINLINK_ABI)
       try:
            price = contract.functions.latestAnswer().call()
            return price / 10**8
       except:
            _, price, _, _, _ = contract.functions.latestRoundData().call()
            return price / 10**8
    except Exception as e:
        logging.warning(f"Price fetch failed: {str(e)}")
        try:
            # Fallback to CoinGecko
            response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": "ethereum", "vs_currencies": "usd"},
                timeout=5
            )
            return response.json()["ethereum"]["usd"]
        except:
            logging.error("All price sources failed, using $1800 default")
            return 1800

def check_rebalance():
    """Rebalance portfolio between ETH and USDbC"""
    try:
        eth_balance = get_eth_balance()
        token_balance = get_token_balance()
        eth_price = get_eth_price()
        eth_value = eth_balance * eth_price
        token_value = token_balance
        total_value = eth_value + token_value
        
        if total_value < 0.1:  # $0.10 minimum
            return None
            
        current_eth_ratio = (eth_value / total_value) * 100
        target_ratio = 50  # 50/50 allocation
        
        # Check if rebalance needed
        if abs(current_eth_ratio - target_ratio) > REBALANCE_THRESHOLD:
            if current_eth_ratio > target_ratio:
                # Too much ETH, sell excess
                excess_eth_value = eth_value - (total_value * target_ratio/100)
                eth_to_sell = excess_eth_value / eth_price
                if eth_to_sell > 0.0001:  # Minimum swap amount
                    return swap_eth_for_token(eth_to_sell)
            else:
                # Too much USDbC, buy ETH
                needed_eth_value = (total_value * target_ratio/100) - eth_value
                if needed_eth_value > 0.1:  # $0.10 minimum
                    return swap_token_for_eth(needed_eth_value)
        return None
    except Exception as e:
        logging.exception("Rebalance failed")
        return None