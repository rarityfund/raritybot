import argparse
from summoner import Summoner

DEFAULT_KEY_FILE = "privatekeyencrypted.json"

def create_parser():
    """Create rarity CLI parser"""

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
    parser = argparse.ArgumentParser(description='Manage your rarity summoners')

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
                        default = "", required = True)
    parser_transfer.add_argument('--to', dest = "to_id", required = True,
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
    parser_transfer_all.add_argument('--to', dest = "to_id", required=True,
                        help='''ID of receiving summoner. Required. 
                        If the summoner does not belong to the current address, the transfer will abort for safety.
                        Use `--force` to send funds to summoners on another address.''',
                        default = "")
    parser_transfer_all.add_argument('--force',  help='''Force transfer to proceed. 
                        Needed to transfer assets to a summoner not owned by this address.''',
                        action = "store_true")

    return parser