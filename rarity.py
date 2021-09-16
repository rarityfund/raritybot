from key import InvalidInputError, load_address, unlock_private_key
from colorama import Fore
import os.path

# Local modules
import key
from transacter import Transacter
import contracts


TIME_OUT = 360
PRIVATE_KEY_FILE = "privatekeyencrypted.json"

def print_intro():
    print(Fore.RED + 'Welcome to Rarity bot V0.1\n')
    print("This script will:")
    print("- Automatically call adventure function if your summoner is ready")
    print("- Automatically level up your summoners")
    print("- Automatically claim gold")
    print("- If your summoner can, automatically makes him do The Cellar dungeon")
    print("\n")

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

    # The transacter will handle the signing and executing of transactions
    transacter = Transacter(owner_address, private_key)

    print("Scanning for summoners...\n")
    summoners = contracts.list_summoners(owner_address, transacter)

    if not summoners:
        print("This address doesn't contains any rarities, bot is exiting...")
        exit()

    print("Here is the list of your summoners :")
    for summoner in summoners:
        print(Fore.LIGHTGREEN_EX + str(summoner))
    print("\n")

    print("Looking for things to do ...")

    for summoner in summoners:        
        # Adventure (only if available)
        summoner.adventure()

        # If possible, level up
        summoner.level_up()

        # If possible, claim gold
        summoner.claim_gold()

        # If possible, farm The Cellar
        summoner.go_cellar()

    print("\n")
    print(Fore.RED + "Our tasks are done now, time to rest, goodbye")
    print(Fore.RED + "Total session cost: " + str(transacter.session_cost) + " FTM")
    

