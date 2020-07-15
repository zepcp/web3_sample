from enum import Enum
from typing import Any, List

from eth_account import Account
from web3 import Web3, HTTPProvider
from web3.contract import Contract
from web3.exceptions import TransactionNotFound
from web3.types import TxReceipt, TxData, EventData, ChecksumAddress, HexStr,\
    TxParams


APPCOINS_ROPSTEN = "0xab949343E6C369C6B17C7ae302c1dEbD4B7B61c3"
APPCOINS_MAINNET = "0x1a7a8BD9106F2B8D977E08582DC7d24c723ab0DB"


INFURA_KEY = "00"
GETH_HOST = "0.0.0.0"
TIMEOUT = 60


class Providers(Enum):
    INFURA_MAINNET = "https://mainnet.infura.io/v3/{}".format(INFURA_KEY)
    INFURA_ROPSTEN = "https://ropsten.infura.io/v3/{}".format(INFURA_KEY)
    GETH = "https://{}:8545".format(GETH_HOST)


class Web3Manager:
    def __init__(self, web3: Web3 = Web3(HTTPProvider(
        Providers.INFURA_ROPSTEN.value, request_kwargs={"timeout": TIMEOUT}))
                 ) -> None:
        self.web3 = web3
        self.gas_limit = 100000
        self.gas_min = 5
        self.gas_max = 50

    @staticmethod
    def to_checksum(wallet: str) -> ChecksumAddress:
        return Web3.toChecksumAddress(wallet)

    @staticmethod
    def create_account() -> (ChecksumAddress, HexStr):
        account = Account.create()
        return account.address, account.privateKey.hex()

    @staticmethod
    def encrypt_account(private_key: HexStr, password: str) -> dict:
        return Account.encrypt(private_key, password)

    @staticmethod
    def decrypt_account(keystore: dict, password: str) -> HexStr:
        return Account.decrypt(keystore, password).hex()

    def get_sync_status(self) -> dict:
        return dict(block=self.web3.eth.blockNumber,
                    gas_price=self.web3.eth.gasPrice,
                    syncing=False if not self.web3.eth.syncing else True,
                    peers=self.web3.net.peerCount)

    def get_gas_price(self) -> int:
        suggested = int(self.web3.eth.gasPrice)
        return self.gas_max if suggested > self.gas_max \
            else suggested if suggested > self.gas_min else self.gas_min

    def get_balance(self, wallet: ChecksumAddress) -> int:
        return self.web3.eth.getBalance(wallet)

    def get_transaction(self, txid: HexStr) -> TxData:
        return self.web3.eth.getTransaction(txid)

    def get_receipt(self, txid: HexStr) -> TxReceipt:
        return self.web3.eth.getTransactionReceipt(txid)

    def has_been_mined(self, txid: HexStr) -> bool:
        try:
            tx_index = self.web3.eth.getTransaction(txid).transactionIndex
            return True if tx_index else False
        except TransactionNotFound:
            return False

    def get_contract_instance(self, address: ChecksumAddress, abi: str
                              ) -> Contract:
        return self.web3.eth.contract(address=address, abi=abi)

    def call_function(self, contract: Contract, func: str, *args) -> Any:
        return contract.functions.__dict__[func](*args).call()

    def get_events_from_receipt(self, contract: Contract, event: str,
                                receipt: TxReceipt) -> List[EventData]:
        return contract.events.__dict__[event]().processReceipt(receipt)

    def get_events(self, contract: Contract, event: str, from_block: int,
                   to_block: int) -> List[EventData]:
        return contract.events.__dict__[event].getLogs(fromBlock=from_block,
                                                       toBlock=to_block)

    def get_transaction_params(self, sender: ChecksumAddress) -> TxParams:
        return {"from": sender,
                "gasPrice": self.get_gas_price(),
                "gas": self.gas_limit,
                "nonce": self.web3.eth.getTransactionCount(sender)}

    def __sign_transaction(self, tx_params: TxParams, private_key: HexStr
                         ) -> HexStr:
        return self.web3.eth.account.signTransaction(tx_params, private_key
                                                     ).rawTransaction

    def __send_transaction(self, raw_transaction: HexStr) -> HexStr:
        return Web3.toHex(self.web3.eth.sendRawTransaction(raw_transaction))

    def send_eth(self, sender: ChecksumAddress, private_key: HexStr,
                 receiver: ChecksumAddress, amount: int) -> HexStr:
        tx_params = {**self.get_transaction_params(sender),
                     "to": Web3.toChecksumAddress(receiver),
                     "value": amount}

        raw_transact = self.__sign_transaction(tx_params, private_key)
        return self.__send_transaction(raw_transact)

    def launch_function(self, contract: Contract, func: str,
                        sender: ChecksumAddress, private_key: HexStr, *args
                        ) -> HexStr:
        tx_params = contract.functions.__dict__[func](*args).buildTransaction(
            self.get_transaction_params(sender))

        raw_transact = self.__sign_transaction(tx_params, private_key)
        return self.__send_transaction(raw_transact)
