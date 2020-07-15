from web3_manager import Web3Manager, APPCOINS_ROPSTEN
from web3.types import HexStr

web3py = Web3Manager()

sender = web3py.to_checksum("0x31a16adf2d5fc73f149fbb779d20c036678b1bbd")
txid = HexStr("0xf87bd91e8d9974792ab9799ac5550ed024117f05ecf28697ca2083bb6a5edafa")
receiver = web3py.to_checksum("0x31a16adf2d5fc73f149fbb779d20c036678b1bbd")
amount = 1
private_key = HexStr("0x")
from_block = 7798718
to_block = 7798718

sync_status = web3py.get_sync_status()
print(sync_status)

gas_price = web3py.get_gas_price()
print(gas_price)

eth_balance = web3py.get_balance(sender)
print(eth_balance)

transaction = web3py.get_transaction(txid)
print(transaction)

receipt = web3py.get_receipt(txid)
print(receipt)

tx_mined = web3py.has_been_mined(txid)
print(tx_mined)

with open("appcoins_ropsten.abi", "r") as f_handler:
    appcoins_abi = f_handler.read()
    f_handler.close()

appcoins = web3py.get_contract_instance(APPCOINS_ROPSTEN, appcoins_abi)

appc_balance = web3py.call_function(appcoins, "balanceOf", sender)
print(appc_balance)

transaction_events = web3py.get_events_from_receipt(appcoins, "Transfer",
                                                    receipt)
print(transaction_events)

block_events = web3py.get_events(appcoins, "Transfer", from_block, to_block)
print(block_events)

txid = web3py.send_eth(sender, private_key, receiver, amount)
print(txid)

txid = web3py.launch_function(appcoins, "transfer", sender, private_key,
                              receiver, amount)
print(txid)
