from summoner import Summoner
from colorama import Fore
import os.path
import argparse

# Local modules
import key
from transacter import Transacter
from list_summoners import list_summoners

DEFAULT_KEY_FILE = "privatekeyencrypted.json"

def print_intro():
    print(Fore.RED + 'Welcome to Rarity bot V1.1')

def create_parser():
    parser = argparse.ArgumentParser(description='Manage your rarity summoners')
    # Main command to direct what we do for that session
    parser.add_argument("command", default = "run", choices = ["run", "list", "summon", "check_gas"],
                        help='''Main command:
                        "run" to run the bot (configure with --actions),
                        "list" to simply list summoners,
                        "summon" to create new summoners (configure with -n and --class)
                        "check_gas" to show price in FTM of common actions,
                        ''',
                        ) 

    # Authentication-related arguments: keyfile, password, import-key
    parser.add_argument('-k', '--keyfile', help='Path to encrypted keyfile', 
                        default = DEFAULT_KEY_FILE)
    parser.add_argument('-p', '--password', help='''Password to decrypt the keyfile. 
                        Be aware it will be available in plaintext in the shell history. 
                        Use of interactive login is preferable if possible.''', default = '')
    parser.add_argument('--import-key', help='''Import a private key which will be stored 
                        encrypted in `privatekeyencrypted.json`''', 
                        action = 'store_true')

    # General config arguments: txmode
    parser.add_argument('--txmode', help='''How transactions are processed. 
                                            "legacy" to send them one by one and wait for the receipt each time.
                                            "batch" to send tx in batches and wait less often''',
                        default = "legacy")
    
    # Command RUN takes argument --actions:
    parser.add_argument('-a', '--actions', help='''All actions to take. Will do everything by default.
                                                   Select one or more from 
                                                   "list" (list Summoners on address), 
                                                   "adventure", 
                                                   "level_up", 
                                                   "claim_gold", 
                                                   "cellar" (send to cellar dungeon)''',
                        nargs='*', default = ["list", "adventure", "level_up", "claim_gold", "cellar"])

    # Command SUMMON takes argument --class and optionally -n
    parser.add_argument('--class', dest = "summoner_class", # cannot use 'class' as var name in python
                        help='''Class used for summoning. Required if command is "summon".
                                Can be class ID (1 to 11) or class name (e.g. "Bard").''',
                        default = "")
    parser.add_argument('-n', '--count', help='Number of summoners to create if command is "summon". Default is 1',
                        default = 1, type = int)
    return parser

if (__name__ == "__main__"):

    # Parsing CLI args
    parser = create_parser()
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

    if args.command == "check_gas":
        # Just printing gas costs and exiting
        transacter.print_gas_price()
    elif args.command == "summon":
        # Summoning new summoners -- need class to be provided
        if args.txmode == "batch":
            print("Error: txmode 'batch' is not available for command 'summon'")
        elif not args.summoner_class:
            print("Error: need class to summon. Pass it with `--class`.")
        else:
            summoner_ids = []
            for i in range(args.count):
                print(Fore.WHITE + "Creating new summoner of class " + str(args.summoner_class))
                new_id = transacter.summon_from_class(args.summoner_class)
                summoner_ids.append(new_id)
            print(Fore.YELLOW + "Created " + str(len(summoner_ids)) + " summoner" + "s" if len(summoner_ids) > 1 else "" + ":")
            for token_id in summoner_ids:
                print(Summoner(token_id, transacter).get_details())
    elif args.command == "list":
        list_summoners(owner_address, transacter, verbose = True)
    elif args.command == "run":
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
    else:
        print(Fore.RED + "Unrecognised command")    
        
    # Wait for all tx to complete (just in case!)
    transacter.wait_for_pending_transations()
    print("\n" + Fore.RED + "Total session cost: " + str(round(transacter.session_cost, 6)) + " FTM")
    

