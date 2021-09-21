from colorama import Fore
import os.path
import argparse

# Local modules
import key
import commands
import cliparser
from transacter import Transacter

def print_intro():
    print(Fore.RED + 'Welcome to Rarity bot v1.2.0.9000 (devel version)')

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
    parser = cliparser.create_parser()
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
        You can import a new key (to create a new keyfile) with the `import-key` command:
        `python3 rarity.py import_key`
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
        commands.command_show(args, transacter)

    ### SUMMON NEW SUMMONERS -----
    elif args.command == "summon":
        commands.command_summon(args, transacter)

    # RUN ACTIONS --------------
    elif args.command == "run":
        commands.command_run(args, transacter)
        
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
    

