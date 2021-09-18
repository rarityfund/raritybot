from colorama import Fore
import os.path
import argparse

# Local modules
import key
from transacter import Transacter
from list_summoners import list_summoners

DEFAULT_KEY_FILE = "privatekeyencrypted.json"

def print_intro():
    print(Fore.RED + 'Welcome to Rarity bot V1.1\n')
    print("This script will:")
    print("- Send your summoners on adventures, if they're ready")
    print("- Level up your summoners when it's time")
    print("- Claim gold on their behalf if any is available")
    print("- Send your summoners to the Cellar dungeon, if they beat it")
    print("\n")


if (__name__ == "__main__"):

    # Parsing CLI args
    parser = argparse.ArgumentParser(description='Manage your rarity summoners')
    parser.add_argument('-k', '--keyfile', help='Path to encrypted keyfile', 
                        default = DEFAULT_KEY_FILE)
    parser.add_argument('-p', '--password', help='''Password to decrypt the keyfile. 
                        Be aware it will be available in plaintext in the shell history. 
                        Use of interactive login is preferable if possible.''', default = '')
    parser.add_argument('-i', '--import-key', help='''Import a private key which will be stored 
                        encrypted in `privatekeyencrypted.json`)''', 
                        action = 'store_const', const = True, default = False)
    parser.add_argument('-a', '--actions', help='''All actions to take. Will do everything by default.
                                                   Select one or more from 
                                                   "list", "adventure", "level_up", "claim_gold", "cellar", "check_gas"''',
                        nargs='*', default = ["list", "adventure", "level_up", "claim_gold", "cellar"])
    parser.add_argument('-t', '--txmode', help='''How transactions are processed. 
                                            "legacy" to send them one by one and wait for the receipt each time.
                                            "batch" to send tx in batches and wait less often''',
                        default = "legacy")
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
            # If pwd was passed as arg, we use it
            private_key = key.load_private_key(args.keyfile, args.password)
        else:
            # Otherwise we prompt the user to unlock the file
            private_key = key.unlock_private_key(args.keyfile)
        owner_address = key.load_address(args.keyfile)
    except key.InvalidInputError as e:
        print(e)
        exit()

    print(Fore.WHITE + "ADDRESS FOUND, Opening " + owner_address + "\n")

    # The transacter will handle the signing and executing of transactions
    transacter = Transacter(owner_address, private_key, txmode = args.txmode)


    if "check_gas" in args.actions:
        transacter.print_gas_price()

    print("Scanning for summoners...\n")
    print_list = "list" in args.actions
    summoners = list_summoners(owner_address, transacter, verbose = print_list)
    print("\n")

    if not summoners:
        print("This address doesn't contains any rarities, bot is exiting...")
        exit()

    print("Looking for things to do ...")

    # We process each action entirely before moving to the next one
    # This is important as, this way, we can wait for tx status only once at the end of a batch
    # This way, level_up will "see" the correct XP and claim_gold will "see" the correct level

    if "adventure" in args.actions:
        print("Checking adventures...")
        for summoner in summoners:        
            summoner.adventure()
        transacter.wait_for_pending_transations()

    if "level_up" in args.actions:
        print("Checking level-up...")
        for summoner in summoners:
            summoner.level_up()
        transacter.wait_for_pending_transations()
    
    if "claim_gold" in args.actions:
        print("Checking gold claims...")
        for summoner in summoners:
            summoner.claim_gold()
        transacter.wait_for_pending_transations()

    if "cellar" in args.actions:
        print("Checking cellar loot...")
        for summoner in summoners:
            summoner.go_cellar()
        transacter.wait_for_pending_transations()
    
    # Wait for all tx to complete
    transacter.wait_for_pending_transations()

    print("\n")
    print(Fore.RED + "Our tasks are done now, time to rest, goodbye")
    print(Fore.RED + "Total session cost: " + str(transacter.session_cost) + " FTM")
    

