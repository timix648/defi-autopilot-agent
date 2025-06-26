import time
import schedule
from flask import session
import logging
from wallet import w3, get_agent_address, get_token_balance, get_eth_balance
from dca import swap_eth_for_token, swap_token_for_eth
from yield_farm import stake_token
from rebalance import check_rebalance
from config import DAILY_ETH_DCA
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

AGENT_ADDRESS = get_agent_address()

TRANSACTION_LOG = []

def log_transaction(tx_hash, description, status="success"):
    global TRANSACTION_LOG
    """Track transactions for dashboard"""
    tx_data = {
        "hash": tx_hash.hex() if hasattr(tx_hash, 'hex') else tx_hash,
        "description": description,
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": status
    }
    TRANSACTION_LOG.append(tx_data)
    return tx_data

def execute_dca():
    logging.info("🚀 Starting DCA cycle...")
    
    demo_mode = session.get('demo_mode', False)
    
    if demo_mode:
        logging.info("🚀 Starting DEMO DCA cycle...")
        try:
            swap_tx = "0x" + "d" * 64
            stake_tx = "0x" + "e" * 64

            log_transaction(swap_tx, f"DEMO: Swapped {DAILY_ETH_DCA} ETH for USDbC")
            log_transaction(stake_tx, f"DEMO: Staked 100.00 USDbC")
            
            logging.info(f"✅ DEMO: Executed DCA cycle")
            return
        except Exception as e:
            logging.exception(f"💥 DEMO execution failed")
    
    if not get_agent_address():
        logging.warning("⏳ Wallet not connected - skipping DCA")
        return
    try:
        swap_tx = swap_eth_for_token(DAILY_ETH_DCA)
        if swap_tx:
            tx_data = log_transaction(swap_tx, f"DCA: Swapped {DAILY_ETH_DCA} ETH for USDbC")
            logging.info(f"✅ Swapped {DAILY_ETH_DCA} ETH for USDbC: {tx_data['hash']}")
            receipt = w3.eth.wait_for_transaction_receipt(swap_tx, timeout=120)
            if receipt.status == 1:
                token_balance = get_token_balance()
                if token_balance > 0:
                    stake_tx = stake_token(token_balance)
                    if stake_tx:
                        log_transaction(stake_tx, f"Staked {token_balance:.2f} USDbC")
                        logging.info(f"🔒 Staked {token_balance:.2f} USDbC")
                rebalance_result = check_rebalance()
                if rebalance_result:
                    log_transaction(rebalance_result, "Portfolio rebalanced")
            else:
                logging.error("❌ Swap transaction failed")
        else:
            logging.error("❌ Swap transaction not sent")
    except Exception as e:
        logging.exception(f"💥 DCA execution failed")
    logging.info("🏁 DCA cycle completed")
schedule.every().day.at("09:00").do(execute_dca)

if __name__ == "__main__":
    logging.info(f"\n{'='*50}")
    logging.info(f"🚀 AutoPilot Agent Started")
    logging.info(f"🔐 Agent Wallet: {AGENT_ADDRESS}")
    logging.info(f"⏰ DCA Schedule: Daily at 09:00 UTC")
    logging.info(f"💵 Daily DCA Amount: {DAILY_ETH_DCA} ETH")
    logging.info(f"{'='*50}\n")
    
    try:
        logging.info(f"💰 ETH Balance: {get_eth_balance():.4f}")
        logging.info(f"💵 USDbC Balance: {get_token_balance():.2f}")
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logging.info("🛑 Agent stopped by user")