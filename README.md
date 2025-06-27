# DeFi Autopilot Agent - CDP Wallet Hackathon
> Self-flying portfolio management with CDP Wallet security

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Overview
BasePilot is an autonomous agent that manages your DeFi assets on Base chain:
- Automated dollar-cost averaging (DCA) of ETH to USDbC
- Yield farming on Extra Finance
- Portfolio rebalancing (50/50 ETH/USDbC)
- Secure transaction signing via CDP Wallet
- Real-time performance dashboard

## ✨ Features
- **One-Click Demo Mode**: Test without real funds
- **Scheduled Execution**: Daily DCA at 9AM UTC
- **Portfolio Rebalancing**: Maintains optimal asset allocation
- **Real-Time Dashboard**: Monitor balances, prices, and transactions
- **CDP Wallet Integration**: Enterprise-grade security

## 🛠 Tech Stack
- **Blockchain**: Base Sepolia
- **Backend**: Python, Flask, Web3.py
- **Frontend**: Bootstrap, Socket.IO
- **Smart Contracts**: Aerodrome (swaps), Extra Finance (staking)
- **Security**: CDP Wallet transaction signing

## ⚙️ Setup (Follow These Steps)

### 1. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate
# Mac/Linux
python3 -m venv venv
source venv/bin/activate

### 2. Install Dependencies (Mandatory)
```markdown
```bash
pip install -r requirements.txt

### 3. Run Application (Mandatory)
```markdown
```bash
python app.py
python agent.py
Access the dashboard at: http://localhost:5000