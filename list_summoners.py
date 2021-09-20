from colorama import Fore
from tabulate import tabulate
import requests

# Class Summoner is defined in summoner.py
from summoner import Summoner

def list_summoners(address, transacter, verbose = True):
    '''List summoners by checking incoming and outgoing ERC721 tx on FTscan'''
    
    print("Scanning for summoners, this may take a while...")

    # Check all ERC721 transactions from account using FTScan API
    erc721transfers_url = "https://api.ftmscan.com/api?module=account&action=tokennfttx&address=" + \
        address + "&startblock=0&endblock=999999999&sort=asc"

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


    # Finally, we instantiate a Summoner for each ID
    summoners = []
    for id in rarities_tokenid_list:
        summoner = Summoner(id, transacter)
        summoners.append(summoner)

    print(Fore.GREEN + "Found " + str(len(summoners)) + " summoners!\n")
    
    # Print data if verbose
    if verbose:
        summoner_data = [summoner.get_details() for summoner in summoners]
        tbl = tabulate(summoner_data, headers = "keys", tablefmt = "fancy")
        print(Fore.WHITE + tbl)

    return summoners

