from colorama import Fore
import os.path
import argparse

# Local modules
import key
from summoner import Summoner
from transacter import Transacter
from list_summoners import list_summoners
from summoning import SummoningEngine

DEFAULT_KEY_FILE = "privatekeyencrypted.json"

def print_intro():
    print(Fore.RED + 'Welcome to Rarity bot v1.2.0.9000 (devel version)')

def create_parser():

    # Putting shared arguments in a shared parser used as parent
    shared_parser = argparse.ArgumentParser(add_help=False)
    # General config/auth arguments: keyfile, password, txmode
    config_group = shared_parser.add_argument_group('configuration')
    config_group.add_argument('-k', '--keyfile', help='Path to encrypted keyfile', 
                        default = DEFAULT_KEY_FILE)
    config_group.add_argument('-p', '--password', help='''Password to decrypt the keyfile. 
                        Be aware it will be available in plaintext in the shell history. 
                        Use of interactive login is preferable if possible.''', default = '')
    config_group.add_argument('--txmode', help='''How transactions are processed. 
                        "single" to send them one by one and wait for the receipt each time.
                        "batch" to send tx in batches and wait less often.''',
                        default = "single", choices = ["single", "batch"])


    # This is the top level parser to which we'll add subparsers
    parser = argparse.ArgumentParser(description='Manage your rarity summoners', parents=[shared_parser])

    # Subparsers: one for each command!
    subparsers = parser.add_subparsers(title = "Commands", dest = "command")
 
    # Command IMPORT_KEY:
    parser_import_key = subparsers.add_parser("import_key", help = "Import a new private key.")
    parser_import_key.add_argument("--keyfile", help = "File path where key will be stored encrypted. " + \
                            "Default location: " + DEFAULT_KEY_FILE,
                            default = DEFAULT_KEY_FILE)
    
     # Command LIST takes argument 'what':
    parser_list = subparsers.add_parser("show", aliases = ["list"], parents = [shared_parser],
                        help = "Show/list a variety of things, like gas price or summoners.")
    parser_list.add_argument("what", help = "What to show. By default, list summoners.", nargs = '?',
                        choices = ["summoners", "gas"], default = "summoners")

    # Command RUN takes argument --actions:
    parser_run = subparsers.add_parser("run", parents=[shared_parser],
                        help = "Run the bot to take automatic configurable actions.")
    parser_run.add_argument('actions', help='''Actions to take. Will do everything by default.
                        Select one or more from 
                        "list" (list Summoners on address), 
                        "adventure", 
                        "level_up", 
                        "claim_gold", 
                        "cellar" (send to cellar dungeon)''',
                        nargs='*', default = ["list", "adventure", "level_up", "claim_gold", "cellar"])

    # Command SUMMON takes argument --class and optionally -n
    parser_summon = subparsers.add_parser("summon", parents=[shared_parser],
                        help = "Summon new summoners of a given class and optionally set attributes.")
    parser_summon.add_argument('summoner_class', # cannot use 'class' as var name in python
                        help='''Class used for summoning. Required.''',
                        choices=Summoner.classes[1:12], default = "")
    parser_summon.add_argument('--attributes', dest = "attributes",
                        help='''Json-formatted attributes to assign after summoning.
                        If not provided, attributes won't be assigned. Should look like: 
                        '{"str":8, "dex":8, "const":8, "int":8, "wis":8, "cha":8}'. 
                        The assignment must cost 32 AP to buy to be valid (you will be warned if it's not the case).
                        ''',
                        default = "")
    parser_summon.add_argument('-n', '--count', help='Number of summoners to create. Default is 1',
                        default = 1, type = int)

    # Command TRANSFER --from, --to and --amount
    parser_transfer = subparsers.add_parser("transfer", parents=[shared_parser],
                        help = "Transfer ERC20 assets between summoners.")
    parser_transfer.add_argument('what', help='''What to transfer. One of "gold" or "craft1" for Crating Material (I).''',
                        choices = ["gold", "craft1"])
    parser_transfer.add_argument('--from', dest = "from_id", # cannot use 'from' as var name in python
                        help='''ID of sending summoner or "all" in which case 
                        ALL summoners at that address will perform the transfer. Required.''',
                        default = "")
    parser_transfer.add_argument('--to', dest = "to_id",
                        help='''ID of receiving summoner. Required. 
                        If the summoner does not belong to the current address, the transfer will abort for safety.
                        Use `--force` to send funds to summoners on another address.''',
                        default = "")
    parser_transfer.add_argument('-n', '--amount', help='Amount to transfer (int).',
                        default = 0, type = int)
    parser_transfer.add_argument('--force',  help='''Force transfer to proceed. 
                        Needed to transfer assets to a summoner not owned by this address.''',
                        action = "store_true")

    # Command TRANSFER_ALL --from, --to and --amount
    parser_transfer_all = subparsers.add_parser("transfer_all", parents=[shared_parser],
                        help = "Transfer all of an ERC20 asset to a particular summoner.")
    parser_transfer_all.add_argument('what', help='''What to transfer. One of "gold" or "craft1" for Crating Material (I).''',
                        choices = ["gold", "craft1"])
    parser_transfer_all.add_argument('--from', dest = "from_id", # cannot use 'from' as var name in python
                        help='''Optional ID of sending summoner. 
                        Typically omitted, in which case ALL summoners at that address will perform the transfer!''', 
                        default = "all")
    parser_transfer_all.add_argument('--to', dest = "to_id",
                        help='''ID of receiving summoner. Required. 
                        If the summoner does not belong to the current address, the transfer will abort for safety.
                        Use `--force` to send funds to summoners on another address.''',
                        default = "")
    parser_transfer_all.add_argument('--force',  help='''Force transfer to proceed. 
                        Needed to transfer assets to a summoner not owned by this address.''',
                        action = "store_true")

    return parser

def get_address_from_args(args):
    try:
        owner_address = key.load_address(args.keyfile)
    except key.InvalidInputError as e:
        print(e)
        exit()
    print(Fore.WHITE + "ADDRESS FOUND, Opening " + owner_address + "\n")
    return owner_address

        
def get_private_key_from_args(args):
    try:
        if args.password != '':
            # If pwd was passed as arg, we use it
            private_key = key.load_private_key(args.keyfile, args.password)
        else:
            # Otherwise we prompt the user to unlock the file
            private_key = key.unlock_private_key(args.keyfile)
    except key.InvalidInputError as e:
        print(e)
        exit()
    return private_key

if (__name__ == "__main__"):

    # Parsing CLI args
    parser = create_parser()
    args = parser.parse_args()

    print_intro()

    # If the user wants to import a new key, we import and exit
    if args.command == "import_key":
        try:
            key.import_new_privatekey(args.keyfile)
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
           
    # Create transacter from address and private_key (the latter only if we need to sign tx)
    # The transacter will handle the signing and executing of transactions
    owner_address = get_address_from_args(args)
    if args.command in ["show", "list"]:
        # Don't need the private key for that
        transacter = Transacter(owner_address, private_key = None, txmode = args.txmode)
    else:
        private_key = get_private_key_from_args(args)
        transacter = Transacter(owner_address, private_key = private_key, txmode = args.txmode)


    # Running the main command

    ### LIST THINGS -----------
    if args.command in ["show", "list"]:
        if args.what == "summoners":
            # Listing summoners
            list_summoners(owner_address, transacter, verbose = True)
        elif args.what == "gas": 
            # Printing gas price and action costs
            transacter.print_gas_price()

    ### SUMMON NEW SUMMONERS -----
    elif args.command == "summon":
        # Summoning new summoners
        summoning_engine = SummoningEngine(transacter)

        # Parse attributes if provided
        summoning_attributes = None
        if args.attributes:
            try:
                summoning_attributes = summoning_engine.parse_attributes(args.attributes)
            except key.InvalidInputError as e:
                print(Fore.RED + str(e))
                exit()

        if not args.summoner_class:
            # Class must be provided
            print("Error: need class to summon. Pass it with `--class`.")

        elif args.txmode == "batch":
            # In batch mode, we won't have the summoner ids until we get the receipts at the end
            for i in range(args.count):
                print(Fore.WHITE + "Creating new summoner of class " + str(args.summoner_class))
                summoning_engine.summon_from_class(args.summoner_class)
            receipts = transacter.wait_for_pending_transations()
            print(Fore.YELLOW + "Created " + str(len(receipts)) + " summoner" + "s" if len(receipts) > 1 else "" + ":")
            summoner_ids = []
            for receipt in receipts:
                summon_details = summoning_engine.get_details_from_summon_receipt(receipt)
                if summon_details:
                    print(Summoner(summon_details["token_id"], transacter).get_details())
                    summoner_ids.append(summon_details["token_id"])
                else:
                    print("Could not get summon data - CANNOT ASSIGN ATTRIBUTES")
            # Now assigning attributes if provided
            if summoning_attributes:
                for summoner_id in summoner_ids:
                    summoning_engine.set_attributes(summoner_id, summoning_attributes)
                receipts2 = transacter.wait_for_pending_transations()

        else:
            # Not in batch mode, so we get the summoner ids as we go
            summoner_ids = []
            for i in range(args.count):
                print(Fore.WHITE + "Creating new summoner of class " + str(args.summoner_class))
                new_id = summoning_engine.summon_from_class(args.summoner_class)
                summoner_ids.append(new_id)
                summoning_engine.set_attributes(new_id, summoning_attributes)
            print(Fore.YELLOW + "Created " + str(len(summoner_ids)) + " summoner" + \
                  ("s" if len(summoner_ids) > 1 else "") + ":")
            
            for token_id in summoner_ids:
                print(Summoner(token_id, transacter).get_details())

    # RUN ACTIONS --------------
    elif args.command == "run":
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
    elif args.command == "transfer":
        # TODO
        pass
    elif args.command == "transfer_all":
        # TODO
        pass
    else:
        print(Fore.RED + "Unrecognised command")    
        
    # Wait for all tx to complete (just in case!)
    transacter.wait_for_pending_transations()
    print("\n" + Fore.RED + "Total session cost: " + str(round(transacter.session_cost, 6)) + " FTM")
    

