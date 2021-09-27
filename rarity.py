from colorama import Fore
import os.path
import argparse

# Local modules
import key
import commands
import cliparser
from transacter import Signer, Transacter
from summoner import InvalidAddressError, InvalidAmountError, InvalidSummonerError

def print_intro():
    print('Welcome to Rarity bot v1.3.2.9000 (devel version)')

def get_address_from_args(args, verbose = True):
    try:
        owner_address = key.load_address(args.keyfile)
    except key.InvalidInputError as e:
        print(Fore.RED + str(e) + Fore.RESET)
        exit()
    if verbose:
        print(Fore.WHITE + "Using address: " + owner_address + "\n")
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
        print(Fore.RED + str(e) + Fore.RESET)
        exit()
    return private_key

def get_signer_from_args(args):
    owner_address = get_address_from_args(args, verbose = False)
    private_key = get_private_key_from_args(args)
    return Signer(owner_address, private_key = private_key)


if (__name__ == "__main__"):

    # Parsing CLI args
    parser = cliparser.create_parser()
    args = parser.parse_args()

    print_intro()

    # If the user wants to import a new key, we import and exit
    if args.command == "import-key":
        try:
            key.import_new_privatekey(args.keyfile)
        except key.InvalidInputError as e:
            print(Fore.RED + str(e) + Fore.RESET)
        exit()

    # If keyfile doesn't exist, we exit
    if not os.path.exists(args.keyfile):
        print("""
        No keyfile found. Specify it with `--keyfile path/to/keyfile.json` or save it as `privatekeyencrypted.json`.
        You can import a new key (to create a new keyfile) with the `import-key` command:
        `python3 rarity.py import-key`
        """ + Fore.RESET)
        exit()
           
    # Create transacter (to handle calls to the blackchain) and signer (to sign tx)
    transacter = Transacter(txmode = args.txmode)

    # Check gas price
    gas_price_gwei = transacter.get_gas_price() * 1e9
    print("Gas price: " + str(round(gas_price_gwei, 1)) + " gwei")
    if gas_price_gwei > args.maxgasprice:
        print(Fore.RED + "Gas price too high (>" + \
            str(round(args.maxgasprice, 1)) + "). Aborting." + Fore.RESET)
        exit()

    # Running the main command

    ### LIST THINGS -----------
    if args.command in ["show", "list"]:
        commands.command_show(args, transacter)

    ### SUMMON NEW SUMMONERS -----
    elif args.command == "summon":
        commands.command_summon(args, transacter)

    # RUN ACTIONS ---------------
    elif args.command == "run":
        commands.command_run(args, transacter)

    # TRANSFER ------------------
    elif args.command in ["transfer", "transfer-all"]:
        try:
            commands.command_transfer(args, transacter, transfer_all = args.command == "transfer-all")
        except (InvalidAmountError, InvalidSummonerError) as e:
            print(Fore.RED + str(e))

    # SEND-SUMMONER --------------
    elif args.command == "send-summoner":
        try:
            commands.command_send_summoner(args, transacter)
        except (InvalidAddressError, InvalidSummonerError) as e:
            print(Fore.RED + e)

    else:
        print(Fore.RED + "Unrecognised command")    
        
    # Wait for all tx to complete (just in case!)
    transacter.wait_for_pending_transations()
    print("\n" + Fore.RED + "Total session cost: " + str(round(transacter.session_cost, 6)) + " FTM" + Fore.RESET)
    

