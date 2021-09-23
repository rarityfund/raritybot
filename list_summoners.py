from colorama import Fore
from tabulate import tabulate
import requests
from transacter import Transacter

# Class Summoner is defined in summoner.py
from summoner import Summoner

def list_tokens_from_contract(owner_address, contract_address):
    """List tokens by listing ERC721 transactions"""

    owner_address = owner_address.lower()
    contract_address = contract_address.lower()
    
    # Check all ERC721 transactions from account using FTScan API
    erc721transfers_url = "https://api.ftmscan.com/api?module=account&action=tokennfttx&address=" + \
        owner_address + "&startblock=0&endblock=999999999&sort=asc"

    try:
        res = requests.get(erc721transfers_url)
        res_json = res.json()
        transfers = res_json["result"]
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    # Loop through ERC721 transactions and count token sent and received
    token_counts = {}

    for transaction in transfers:
        if transaction["contractAddress"] == contract_address:
            token_id = int(transaction["tokenID"])
            if transaction["to"] == owner_address:
                token_counts[token_id] = token_counts.get(token_id, 0) + 1
            if transaction["from"] == owner_address:
                token_counts[token_id] = token_counts.get(token_id, 0) - 1

    # Tokens we still own should have a count of 1 (we could have sent them and gotten them back)
    # We should only ever have counts of -1 and +1
    return [token for token in token_counts if token_counts[token] > 0]


def list_summoners(address, transacter, verbose = True):
    '''List summoners owned by the given address'''
    
    print("Scanning for summoners, this may take a while...")
    token_ids = list_tokens_from_contract(address, contract_address = Transacter.contract_addresses["summoner"])

    print(Fore.GREEN + "Found " + str(len(token_ids)) + " summoners!\n")
    print(Fore.WHITE + "Fetching summoner info, this may take a while...\n")
    
    # Finally, we instantiate a Summoner for each ID
    summoners = []
    for id in token_ids:
        summoner = Summoner(id, transacter)
        summoners.append(summoner)

    # Print data if verbose
    if verbose:
        summoner_data = [summoner.get_details() for summoner in summoners]
        tbl = tabulate(summoner_data, headers = "keys", tablefmt = "fancy")
        print(Fore.WHITE + tbl)

    return summoners

