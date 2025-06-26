import os
from web3 import Web3

BASE_RPC_URL = "https://sepolia.base.org" 
CHAIN_ID = 84532  # Base Sepolia

w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))

# Contract addresses (Base Sepolia)
AERODROME_ROUTER = "0x4200000000000000000000000000000000000006"
EXTRA_POOL = "0x1dD2f8d4D9eD0Bf5c5f7aBd53639eFc1832B6cE2"
ETH_USD_FEED = w3.to_checksum_address("0x0d127a2A8a6a4c9b3Ea2D0d13eF3F2C5BdEe7E0F")
TARGET_TOKEN = w3.to_checksum_address("0x036CbD53842c5426634e7929541eC2318f3dCF7e")
WETH_ADDRESS = w3.to_checksum_address("0x4200000000000000000000000000000000000006")
UNISWAP_V3_FACTORY = w3.to_checksum_address("0x33128a8fC17869897dcE68Ed026d694621f6FDfD")
UNISWAP_ETH_USDC_POOL = w3.to_checksum_address("0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1")
EXTRA_POOL = w3.to_checksum_address("0x1dD2f8d4D9eD0Bf5c5f7aBd53639eFc1832B6cE2")  # USDbC pool
TARGET_TOKEN = w3.to_checksum_address("0x036CbD53842c5426634e7929541eC2318f3dCF7e")  # USDbC

DAILY_ETH_DCA = 0.01  # ~$30
REBALANCE_THRESHOLD = 5  # 5% portfolio drift

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "success", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    },
    {
        "inputs": [
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "path", "type": "address[]"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactETHForTokens",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "path", "type": "address[]"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactTokensForETH",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

CHAINLINK_ABI = [
    {
        "inputs": [],
        "name": "latestAnswer",
        "outputs": [{"internalType": "int256", "name": "", "type": "int256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "latestRoundData",
        "outputs": [
            {"internalType":"uint80","name":"roundId","type":"uint80"},
            {"internalType":"int256","name":"answer","type":"int256"},
            {"internalType":"uint256","name":"startedAt","type":"uint256"},
            {"internalType":"uint256","name":"updatedAt","type":"uint256"},
            {"internalType":"uint80","name":"answeredInRound","type":"uint80"}
        ],
        "stateMutability":"view",
        "type":"function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType":"uint8","name":"","type":"uint8"}],
        "stateMutability":"view",
        "type":"function"
    }
]

AERODROME_ABI = [
    {
        "inputs": [
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "path", "type": "address[]"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactETHForTokens",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]

EXTRA_ABI = [
    {
        "name": "deposit",
        "inputs": [
            {"name": "asset", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "outputs": [],
        "type": "function"
    }
]