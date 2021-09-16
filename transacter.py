from web3 import Web3
import contracts

class Transacter:
    """Class in charge of perparing and signing transactions"""

    def __init__(self, address, private_key):
        self.address = address
        self.private_key = private_key
        self.w3 =  Web3(Web3.HTTPProvider('https://rpc.ftm.tools/'))
        self.nonce =  self.w3.eth.get_transaction_count(Web3.toChecksumAddress(self.address))
        # Prepare all contracts only once
        self.contracts = {cname: contracts.get_contract(self.w3, cname) for cname in contracts.contract_addresses.keys()}
        self.session_cost = 0

    def timestamp(self):
        return self.w3.eth.get_block('latest')["timestamp"]

    def get_summoner_info(self, id):
        return self.contracts["summoner"].functions.summoner(id).call()

    def execute(self, call):
        adventure_fun = self.contracts["summoner"].functions.adventure(self.token_id)
        self.transacter.sign_and_execute(adventure_fun, gas = 70000)

    def sign_and_execute(self, w3fun, gas, wait_for_receipt = True, wait_timeout = 360):
        """
        Sign and execute a web3 function call. Returns status as a bool.
        If wait_for_receipt is False, returns True, as if the tx was successful.
        """
        tx = w3fun.buildTransaction({
            'chainId': 250,
            'gas': gas,
            # TODO: gasprice is estimated automatically for now, will need to optimize it later
            'nonce': self.nonce})
        tx_signed = self.w3.eth.account.sign_transaction(tx, private_key = self.private_key)
        self.w3.eth.send_raw_transaction(tx_signed.rawTransaction)
        self.nonce = self.nonce + 1
        tx_hash = self.w3.toHex(self.w3.keccak(tx_signed.rawTransaction))

        estimated_cost = gas * self.w3.eth.gas_price / 1e18
        self.session_cost += estimated_cost
        print("Transaction sent for " + str(estimated_cost) + "FTM, id: " + tx_hash)
        if not wait_for_receipt:
            return True
        else:
            print("Waiting for receipt ...")
            try:
                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, wait_timeout)
            except self.w3.exceptions.TransactionNotFound as e:
                raise SystemExit(e)
            return tx_receipt["status"] == 1
