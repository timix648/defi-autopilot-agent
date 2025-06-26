import os
from flask import Flask, render_template, jsonify, redirect, session, request
from flask_socketio import SocketIO
import threading
import time
from flask import send_from_directory
from agent import execute_dca, TRANSACTION_LOG
from wallet import get_eth_balance, get_token_balance, get_agent_address, save_agent_address
import wallet
from rebalance import get_eth_price
import config
from web3 import Web3
import logging
from datetime import datetime

app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static',
            template_folder='templates')
app.secret_key = os.urandom(24)
w3 = Web3(Web3.HTTPProvider(config.BASE_RPC_URL))

agent_state = {
    "status": "running",
    "last_execution": None,
    "next_execution": time.strftime("%Y-%m-%d 09:00:00"),
    "eth_balance": 0,
    "token_balance": 0,
    "eth_price": 0,
    "transactions": [],
    "agent_address": None,
    "demo_mode": False
}

def update_balances():
    try:
        current_address = wallet.get_agent_address()
        agent_state["agent_address"] = current_address
        
        if current_address:
            agent_state["eth_balance"] = get_eth_balance()
            agent_state["token_balance"] = get_token_balance()
            agent_state["eth_price"] = get_eth_price()
        else:
            agent_state["eth_balance"] = 0
            agent_state["token_balance"] = 0
            agent_state["eth_price"] = 0
            
        agent_state["transactions"] = list(TRANSACTION_LOG)
    except Exception as e:
        logging.error(f"Balance update error: {e}")

socketio = SocketIO(app, async_mode='threading')

@app.route('/')
def dashboard():
    update_balances()
    agent_state["agent_address"] = wallet.get_agent_address()
    agent_state["demo_mode"] = session.get('demo_mode', False)
    return render_template('dashboard.html', state=agent_state)

@app.route('/connect')
def connect_wallet():
    try:
        address = "0xSIM" + os.urandom(20).hex()
        session['agent_address'] = address
        save_agent_address(address)
        
        agent_state.update({
            "agent_address": address,
            "demo_mode": False
        })
        
        socketio.emit('update', agent_state)
        return jsonify({"status": "connected"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/connect_demo', methods=['POST'])
def connect_demo():
    try:
        demo_account = w3.eth.account.create()
        agent_state.update({
            "agent_address": demo_account.address,
            "demo_mode": True,
            "eth_balance": 1.0,
            "token_balance": 1800.0,
            "eth_price": 1800.0,
            "transactions": []
        })
        return jsonify({ 
            "status": "success",
            "state": agent_state
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def agent_worker():
    while True:
        try:
            emit_state_update()
        except Exception as e:
            print(f"Background error: {e}")
        time.sleep(10)

def emit_state_update():
    update_balances()
    socketio.emit('update', agent_state)

@socketio.on('connect')
def handle_connect():
    emit_state_update()

@app.route('/toggle', methods=['POST'])
def toggle_agent():
    agent_state["status"] = "paused" if agent_state["status"] == "running" else "running"
    return jsonify({"status": agent_state["status"]})

@app.route('/execute', methods=['POST'])
def manual_execute():
    if agent_state.get('demo_mode'):
        tx_hash = f"0xDEMO{os.urandom(20).hex()}"
        TRANSACTION_LOG.append({
            "hash": tx_hash,
            "description": "DEMO: DCA Execution",
            "time": datetime.now().strftime("%H:%M:%S"),
            "status": "success"
        })
        return jsonify({
            "status": "success",
            "tx_hash": tx_hash
        })
    
    if agent_state["status"] == "running":
        execute_dca()
        agent_state["last_execution"] = time.strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({"executed": agent_state["last_execution"]})

if __name__ == '__main__':
    update_balances()
    threading.Thread(target=agent_worker, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    
@app.route('/clear', methods=['POST'])
def clear_transactions():
    if agent_state.get('demo_mode'):
        agent_state['transactions'] = []
        return jsonify({"status": "cleared"})
    return jsonify({"status": "error"}), 400