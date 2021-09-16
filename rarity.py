from colorama import Fore
import os.path
import argparse

# Local modules
import key
from transacter import Transacter
import contracts

DEFAULT_KEY_FILE = "privatekeyencrypted.json"

def print_intro():
    print(Fore.RED + 'Welcome to Rarity bot V0.1\n')
    print("This script will:")
    print("- Automatically call adventure function if your summoner is ready")
    print("- Automatically level up your summoners")
    print("- Automatically claim gold")
    print("- If your summoner can, automatically makes him do The Cellar dungeon")
    print("\n")


if (__name__ == "__main__"):

    # Parsing CLI args
    parser = argparse.ArgumentParser(description='Manage your rarity summoners')
    parser.add_argument('-k', '--keyfile', help='Path to encrypted keyfile', 
                        default = DEFAULT_KEY_FILE)
    parser.add_argument('-p', '--password', help='''Password to decrypt the keyfile. 
                        Be aware it will be available in plaintext in the shell history. 
                        Use of interactive login is preferable if possible.''', default = '')
    parser.add_argument('--import-key', help='''Import a private key which will be stored 
                        encrypted in `privatekeyencrypted.json`)''', 
                        action = 'store_const', const = True, default = False)
    parser.add_argument('--adventure-only', help='Only call adventure() and nothing else.', 
                        action = 'store_const', const = True, default = False)
    args = parser.parse_args()

    print_intro()

    # If the user wants to import a new key, we import and exit
    if args.import_key:
        try:
            key.import_new_privatekey(DEFAULT_KEY_FILE)
            print("Key imported successfully in " + DEFAULT_KEY_FILE  + " - run the program again to use it.")
        except key.InvalidInputError as e:
            print(e)
        exit()

    # If keyfile doesn't exist, we exit
    if not os.path.exists(args.keyfile):
        print("""
        No keyfile found. Specify it with `--keyfile path/to/keyfile.json` or save it as `privatekeyencrypted.json`.
        You can import a new key (to create a new keyfile) with the `--import-key` flag.
        """)
        exit()
           
    
    # Load account details from keyfile
    try:
        if args.password != '':
            private_key = key.load_private_key(args.keyfile, args.password)
        else:
            private_key = key.unlock_private_key(args.keyfile)
        owner_address = key.load_address(args.keyfile)
    except key.InvalidInputError as e:
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
        if not args.adventure_only:
            # If possible, level up
            summoner.level_up()
            # If possible, claim gold
            summoner.claim_gold()
            # If possible, farm The Cellar
            summoner.go_cellar()

    print("\n")
    print(Fore.RED + "Our tasks are done now, time to rest, goodbye")
    print(Fore.RED + "Total session cost: " + str(transacter.session_cost) + " FTM")
    

