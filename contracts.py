import requests
from web3 import Web3
from colorama import Fore

# Class Summoner is defined in summoner.py
from summoner import Summoner

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

def get_contract(w3, contract_name):
    '''Get contract or raise a KeyError if contract isn't part of the dict'''
    return w3.eth.contract(address=contract_checksums[contract_name], 
                           abi=getAbiFromContractAdress(contract_addresses[contract_name]))

def getAbiFromContractAdress(contractAdress):
    '''Get abi from contract address'''
    abi_contract_url = "https://api.ftmscan.com/api?module=contract&action=getabi&address=" + contractAdress + "&apikey=" + API_FTMSCAN_TOKEN
    try:
        res = requests.get(abi_contract_url)
        res_json = res.json()
        abi = res_json["result"]
        return abi
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

def list_rarities(address):
    '''List rarities by checking incoming and outgoing ERC721 tx on FTscan'''

    # Check all ERC721 transactions from account using FTScan API
    erc721transfers_url = "https://api.ftmscan.com/api?module=account&action=tokennfttx&address=" + address + "&startblock=0&endblock=999999999&sort=asc"

    try:
        res = requests.get(erc721transfers_url)
        res_json = res.json()
        transfers = res_json["result"]
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    # Loop through ERC721 transactions and list tokens still owned by address
    rarities_tokenid_list = []

    # First we populate a list with token that are in "IN" transactions
    for transaction in transfers:
        if transaction["to"] == address:
            rarities_tokenid_list.append(int(transaction["tokenID"]))

    # Then we remove from list the token that are in "OUT" transactions
    for transaction in transfers:
        if transaction["from"] == address:
            rarities_tokenid_list.remove(int(transaction["tokenID"]))

    return rarities_tokenid_list

def list_summoners(address, transacter, verbose = False):
    rarities_tokenid_list = list_rarities(address)

    summoners = []
    for id in rarities_tokenid_list:
        summoner = Summoner(id, transacter)
        summoners.append(summoner)
        if verbose:
            print(Fore.LIGHTGREEN_EX + str(summoner))
    return summoners

