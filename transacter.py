from web3 import Web3
import requests

class Transacter:
    """Class in charge of preparing and signing transactions"""

    # Configuration constants
    API_FTMSCAN_TOKEN = "VU7CVDPWW2GSFM7JWFCIP49AE9EPJVVSC4"

    # Contracts adresses
    contract_addresses = {
        "rarity": "0xce761d788df608bd21bdd59d6f4b54b2e27f25bb",
        "summoner": "0xce761d788df608bd21bdd59d6f4b54b2e27f25bb", # Same as rarity but friendly name
        "gold": "0x2069B76Afe6b734Fb65D1d099E7ec64ee9CC76B2",
        "cellar": "0x2A0F1cB17680161cF255348dDFDeE94ea8Ca196A"
    }

    # Contracts adress checksums
    contract_checksums = {k: Web3.toChecksumAddress(v) for k, v in contract_addresses.items()}

    def __init__(self, address, private_key):
        self.address = address
        self.private_key = private_key
        self.w3 =  Web3(Web3.HTTPProvider('https://rpc.ftm.tools/'))
        self.nonce =  self.w3.eth.get_transaction_count(Web3.toChecksumAddress(self.address))
        # Prepare all contracts only once
        self.contracts = {cname: self.get_contract(cname) for cname in self.contract_addresses.keys()}
        self.session_cost = 0


    def get_contract(self, contract_name):
        '''Get contract or raise a KeyError if contract isn't listed'''
        return self.w3.eth.contract(address = self.contract_checksums[contract_name], 
                               abi = self.get_abi(self.contract_addresses[contract_name]))


    def get_abi(self, contract_address):
        '''Get abi from contract address'''
        abi_contract_url = "https://api.ftmscan.com/api?module=contract&action=getabi&address=" + \
            contract_address + "&apikey=" + self.API_FTMSCAN_TOKEN
        try:
            res = requests.get(abi_contract_url)
            res_json = res.json()
            abi = res_json["result"]
            return abi
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def timestamp(self):
        return self.w3.eth.get_block('latest')["timestamp"]

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
