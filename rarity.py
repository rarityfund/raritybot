

from eth_keyfile import keyfile
from key import InvalidInputError, load_address, unlock_private_key
from eth_utils.hexadecimal import decode_hex
from web3 import Web3
import requests
import statistics
from colorama import Fore, Back, Style
import os.path

# Module key is in key.py
import key

#Const
api_ftmcan_token = "VU7CVDPWW2GSFM7JWFCIP49AE9EPJVVSC4"
TIME_OUT = 360

# Using constant file name for now
PRIVATE_KEY_FILE = "privatekeyencrypted.json"

# Connect to phantom

w3 = Web3(Web3.HTTPProvider('https://rpc.ftm.tools/'))

# Contracts adresses

summoner_contract_addr = "0xce761d788df608bd21bdd59d6f4b54b2e27f25bb" # Rarity contract
rarity_gold_contract_addr = "0x2069B76Afe6b734Fb65D1d099E7ec64ee9CC76B2" # Rarity gold contract
rarity_theCellar_contract_addr = "0x2A0F1cB17680161cF255348dDFDeE94ea8Ca196A" # Rarity The Cellar contract
summoner_contract_addr_checksumed = w3.toChecksumAddress(summoner_contract_addr)
rarity_gold_contract_addr_checksumed = w3.toChecksumAddress(rarity_gold_contract_addr)
rarity_theCellar_contract_addr_checksumed = w3.toChecksumAddress(rarity_theCellar_contract_addr)

def print_intro():
    print(Fore.RED + 'Welcome to Rarity bot V0.1\n')
    print("This script will:")
    print("- Automatically call adventure function if your summoner is ready")
    print("- Automatically level up your summoners")
    print("- Automatically claim gold")
    print("- If your summoner can, automatically makes him do The Cellar dungeon")
    print("\n")

# Get abi from contract function

def getAbiFromContractAdress(contractAdress):
    abi_contract_url = "https://api.ftmscan.com/api?module=contract&action=getabi&address=" + contractAdress + "&apikey=" + api_ftmcan_token
    try:
        res = requests.get(abi_contract_url)
        res_json = res.json()
        abi = res_json["result"]
        return abi
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

# Get class from index

def getClassFromIndex(index):
    summoner_contract = w3.eth.contract(address=summoner_contract_addr_checksumed, 
    abi=getAbiFromContractAdress(summoner_contract_addr))
    summoner_class = summoner_contract.functions.classes(index).call()
    return summoner_class

if (__name__ == "__main__"):
    
    print_intro()

    # If keyfile doesn't exist, we create one or exit
    if not os.path.exists(PRIVATE_KEY_FILE):
        print("No keyfile found. Do you want to import a new address from a private key ? (y or n)")
        if input() != "y":
            exit()
        else:
            try:
                key.import_new_privatekey(PRIVATE_KEY_FILE)
            except InvalidInputError as e:
                print(e)
                exit()
    
    # Load account details from keyfile
    try:
        private_key = key.unlock_private_key(PRIVATE_KEY_FILE)
        owner_address = key.load_address(PRIVATE_KEY_FILE)
    except InvalidInputError as e:
        print(e)
        exit()

    print(Fore.WHITE + "ADDRESS FOUND, Opening " + owner_address + "\n")

    print("Scanning for summoners...\n")

    # Check all ERC721 transactions from account using FTScan API

    erc721transfers_url = "https://api.ftmscan.com/api?module=account&action=tokennfttx&address=" + owner_address + "&startblock=0&endblock=999999999&sort=asc"

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
        if transaction["to"] == owner_address:
            rarities_tokenid_list.append(int(transaction["tokenID"]))

    # Then we remove from list the token that are in "OUT" transactions
    for transaction in transfers:
        if transaction["from"] == owner_address:
            rarities_tokenid_list.remove(int(transaction["tokenID"]))

    # Call contracts to populate all useful info about rarities

    summoners = []
    summoner_contract = w3.eth.contract(address=summoner_contract_addr_checksumed, abi=getAbiFromContractAdress(summoner_contract_addr))
    rarity_gold_contract = w3.eth.contract(address=rarity_gold_contract_addr_checksumed, abi=getAbiFromContractAdress(rarity_gold_contract_addr))
    rarity_theCellar_contract = w3.eth.contract(address=rarity_theCellar_contract_addr_checksumed, abi=getAbiFromContractAdress(rarity_theCellar_contract_addr))


    for id in rarities_tokenid_list:
        #Call summoner method from rarity contract
        summoner_info = summoner_contract.functions.summoner(id).call()
        summoners.append(
            {
                "tokenid": id,
                "class": getClassFromIndex(summoner_info[2]),
                "level": summoner_info[3],
                "xp": summoner_info[0]/1e18
            }
        )
    #Print in a fancy manner all rarities

    if not summoners:
        print("This address doesn't contains any rarities, bot is exiting...")
        exit()

    print("Here is the list of your summoners :")

    for summoner in summoners:
        print(Fore.LIGHTGREEN_EX + "A " + summoner["class"] + ", of level " + str(summoner["level"]) + " with " + str(summoner["xp"]) + " xp")
        
    print("\n")

    print("Looking for things to do ...")
    # Loop through them to call adventure() function

    nonce = w3.eth.get_transaction_count(Web3.toChecksumAddress(owner_address))

    # We start automated workflow for summoners here

    for summoner in summoners:
        
        # adventure()
        if w3.eth.get_block('latest')["timestamp"] > summoner_contract.functions.adventurers_log(summoner["tokenid"]).call():
            print(Fore.WHITE + "A  " + summoner["class"] + ", of level " + str(summoner["level"]) + " has gone into an adventure !")
            adventure_transaction = summoner_contract.functions.adventure(summoner["tokenid"]).buildTransaction({
                'chainId': 250, # Maybe find it automactically from provider
                'gas': 70000,
                # gasprice is estimated automatically for now, will need to optimize it later
                'nonce': nonce
            })
            #adventure_transaction["gasPrice"] = w3.toWei(80,'gwei')
            adventure_transaction_signed = w3.eth.account.sign_transaction(adventure_transaction, private_key=private_key)
            w3.eth.send_raw_transaction(adventure_transaction_signed.rawTransaction)
            nonce = nonce+1
            adventure_transaction_hash = w3.toHex(w3.keccak(adventure_transaction_signed.rawTransaction))
            print("Transaction sent, id : " + adventure_transaction_hash)
            print("Waiting for receipt ...")
            try:
                adventure_transaction_receipt = w3.eth.wait_for_transaction_receipt(adventure_transaction_hash,TIME_OUT)
            except w3.exceptions.TransactionNotFound as e:
                raise SystemExit(e)
            if adventure_transaction_receipt["status"] == 1:
                print("The summoner came back with success from his adventure !")
            else: 
                print("Transaction failed. The summoner prefers to stay at home")

        #If possible, level up
        current_level = summoner_contract.functions.level(summoner["level"]).call()
        current_xp = summoner_contract.functions.xp(summoner["tokenid"]).call()
        xp_required = summoner_contract.functions.xp_required(int(current_level)).call()
        if int(xp_required) <= int(current_xp):
            print("The summoner is attempting to pass a new level !")
            levelup_transaction = summoner_contract.functions.level_up(summoner["tokenid"]).buildTransaction({
                'chainId': 250, # Maybe find it automactically from provider
                'gas': 70000,
                # gasprice is estimated automatically for now, will need to optimize it later
                'nonce': nonce
            })
            levelup_transaction_signed = w3.eth.account.sign_transaction(levelup_transaction, private_key=private_key)
            w3.eth.send_raw_transaction(levelup_transaction_signed.rawTransaction)
            nonce = nonce+1
            levelup_transaction_hash = w3.toHex(w3.keccak(levelup_transaction_signed.rawTransaction))
            print("Transaction sent, id : " + levelup_transaction_hash)
            print("Waiting for receipt ...")
            try:
                adventure_transaction_receipt = w3.eth.wait_for_transaction_receipt(levelup_transaction_hash,TIME_OUT)
            except w3.exceptions.TransactionNotFound as e:
                raise SystemExit(e)
            if adventure_transaction_receipt["status"] == 1:
                print(Fore.YELLOW + "He has passed a new level !")
            else: 
                print(Fore.WHITE + "Transaction failed. The summoner was incapable to pass a new level")

        # If possible, claim gold
        is_gold_claimable = rarity_gold_contract.functions.claimable(summoner["tokenid"]).call()
        if is_gold_claimable > 0:
            print(Fore.WHITE + "A summoner is claiming gold")
            claim_gold_transaction = rarity_gold_contract.functions.claim(summoner["tokenid"]).buildTransaction({
                'chainId': 250, # Maybe find it automactically from provider
                'gas': 120000,
                # gasprice is estimated automatically for now, will need to optimize it later
                'nonce': nonce
            })
            #adventure_transaction["gasPrice"] = w3.toWei(80,'gwei')
            claim_gold_transaction_signed = w3.eth.account.sign_transaction(claim_gold_transaction, private_key=private_key)
            w3.eth.send_raw_transaction(claim_gold_transaction_signed.rawTransaction)
            nonce = nonce+1
            claim_gold_transaction_hash = w3.toHex(w3.keccak(claim_gold_transaction_signed.rawTransaction))
            print("Transaction sent, id : " + claim_gold_transaction_hash)
            print("Waiting for receipt ...")
            try:
                claim_gold_transaction_receipt = w3.eth.wait_for_transaction_receipt(claim_gold_transaction_hash,TIME_OUT)
            except w3.exceptions.TransactionNotFound as e:
                raise SystemExit(e)
            if claim_gold_transaction_receipt["status"] == 1:
                print("The summoner claimed gold with success !")
            else: 
                print("Transaction failed. The summoner prefers to stay at home")



        # If possible, farm The Cellar
        if w3.eth.get_block('latest')["timestamp"] > rarity_theCellar_contract.functions.adventurers_log(summoner["tokenid"]).call():
            if int(rarity_theCellar_contract.functions.scout(summoner["tokenid"]) .call()) > 0:
                print(Fore.WHITE + "The summoner is going to The Cellar")
                adventure_transaction = rarity_theCellar_contract.functions.adventure(summoner["tokenid"]).buildTransaction({
                    'chainId': 250, # Maybe find it automactically from provider
                    'gas': 120000,
                    # gasprice is estimated automatically for now, will need to optimize it later
                    'nonce': nonce
                })
                #adventure_transaction["gasPrice"] = w3.toWei(80,'gwei')
                adventure_transaction_signed = w3.eth.account.sign_transaction(adventure_transaction, private_key=private_key)
                w3.eth.send_raw_transaction(adventure_transaction_signed.rawTransaction)
                nonce = nonce+1
                adventure_transaction_hash = w3.toHex(w3.keccak(adventure_transaction_signed.rawTransaction))
                print("Transaction sent, id : " + adventure_transaction_hash)
                print("Waiting for receipt ...")
                try:
                    adventure_transaction_receipt = w3.eth.wait_for_transaction_receipt(adventure_transaction_hash,TIME_OUT)
                except w3.exceptions.TransactionNotFound as e:
                    raise SystemExit(e)
                if adventure_transaction_receipt["status"] == 1:
                    print("The summoner came back from The Cellar with success !")
                else: 
                    print("Transaction failed. The summoner prefers to stay at home")
        

    print("\n")
    print(Fore.RED + "Our tasks are done now, time to rest, goodbye")


