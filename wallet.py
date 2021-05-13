# Import dependencies
import subprocess
import json
import os
from dotenv import load_dotenv

# Load and set environment variables
load_dotenv()
mnemonic=os.getenv("mnemonic")

# Import constants.py and necessary functions from bit and web3
from constants import BTC, BTCTEST, ETH
from pprint import pprint
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
from web3 import Web3, middleware, Account
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.middleware import geth_poa_middleware

# connecting Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# enabling PoA middleware
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# setting gas price
w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

# including a mnemonic
mnemonic = os.getenv("mnemonic", "put chest all episode penalty twist visual resemble scene december sweet march")

 
# Create a function called `derive_wallets`
def derive_wallets(coin=BTC, mnemonic=mnemonic, depth=3):
    command = "./derive -g --mnemonic='{mnemonic}' --coin={coin} --numderive={depth} --format=json"
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    return json.loads(output)

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {
    ETH: derive_wallets(coin= ETH),
    BTCTEST: derive_wallets(coin=BTCTEST)}

pprint(coins)

# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
     if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
     if coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)

# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(account, coin, amount, to ):
    if coin == ETH:
        value = w3.toWei(amount, "ether") # convert 1.2 ETH to 120000000000 wei
        gasEstimate = w3.eth.estimateGas({ "to": to, "from": account.address, "amount": value })
        return {
            "TO": to,
            "FROM": account.address,
            "VALUE": value,
            "GAS": gasEstimate,
            "GAS_PRICE": w3.eth.gasPrice,
            "NONCE": w3.eth.getTransactionCount(account.address),
            "CHAIN_ID": 333
        }
    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(account, coin, amount, to ):
    if coin == ETH:
        raw_tx = create_tx(coin, account, to, amount)
        signed = account.signTransaction(raw_tx)
        return w3.eth.sendRawTransaction(signed.rawTransaction)
    if coin == BTCTEST:
        raw_tx = create_tx(coin, account, to, amount)
        signed = account.sign_transaction(raw_tx)
        return NetworkAPI.broadcast_tx_testnet(signed)

