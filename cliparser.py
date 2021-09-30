import argparse
from raritydata import RarityData

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
    config_group.add_argument('-g', '--maxgasprice', help='''Optional max gas price (integer in gwei) you're willing to pay. 
    Abort if gas price is superior. Gas price is typically between 100 and 500 gwei.''',
                        default = 10000, type = int)

    # This is the top level parser to which we'll add subparsers
    parser = argparse.ArgumentParser(description='Manage your rarity summoners')

    # Subparsers: one for each command!
    subparsers = parser.add_subparsers(title = "Commands", dest = "command")
 
    # Command IMPORT_KEY:
    parser_import_key = subparsers.add_parser("import-key", help = "Import a new private key.")
    parser_import_key.add_argument("--keyfile", help = "File path where key will be stored encrypted. " + \
                            "Default location: " + DEFAULT_KEY_FILE,
                            default = DEFAULT_KEY_FILE)
    
     # Command SHOW (alias LIST) takes argument 'what':
    show_options = ["summoners", "gas", "skills", "items", "craftable", "crafting-proba"]
    parser_list = subparsers.add_parser("show", aliases = ["list"], parents = [shared_parser],
                        help = "Show/list a variety of things, like gas price or summoners.")
    parser_list.add_argument("what", help = "What to show. By default, list summoners.", nargs = '?',
                        choices = show_options, default = "summoners")
    parser_list.add_argument("-n", "--limit", help = "Limit the number of tokens shown. Optional integer.",
                        default = 0, type = int)
    

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
                        choices=RarityData.class_names[1:12], default = "")
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
    parser_transfer.add_argument('-n', '--amount', help='Required. Amount to transfer (integer).',
                        default = 0, type = int, required = True)
    parser_transfer.add_argument('--force',  help='''Force transfer to proceed. 
                        Needed to transfer assets to a summoner not owned by this address.''',
                        action = "store_true")

    # Command TRANSFER_ALL: almost the same as TRANSFER but different defaults and no amount
    parser_transfer_all = subparsers.add_parser("transfer-all", parents=[shared_parser],
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

    # Command SEND-SUMMONER: almost the same as TRANSFER
    parser_send_summoner = subparsers.add_parser("send-summoner", parents=[shared_parser],
                        help = "Send summoners to another address. Be careful.")
    parser_send_summoner.add_argument('who', help='Who to transfer. Either a summoner ID or "all" to send everyone.')
    parser_send_summoner.add_argument('--to', dest = "to_address", required=True,
                        help='Destination address of new owner, starting with "0x"',
                        default = "")
    parser_send_summoner.add_argument('--force',  help='''Force transfer to proceed. Needed when transferring ALL summoners.''',
                        action = "store_true")

    # Command SET-ATTRIBUTES
    parser_set_attrs = subparsers.add_parser("set-attributes", parents=[shared_parser],
                        help = "Set summoner attributes")
    parser_set_attrs.add_argument('attributes', help='''Json-formatted attributes to assign after summoning.
                        Must look like: 
                        '{"str":8, "dex":8, "const":8, "int":8, "wis":8, "cha":8}'. 
                        The assignment must cost 32 AP to buy to be valid (bot will abort if it's not the case).
                        ''')
    parser_set_attrs.add_argument('summoner_ids', help='''One or more summoner ids whose attributes to set. 
                        Can also be "all", in which case all summoners on the address 
                        who don't already have attributes will get the attributes provided.''', nargs="+")
                    

    # Command SET-SKILL
    parser_set_skill = subparsers.add_parser("set-skill", parents=[shared_parser],
                        help = "Set a skill level")
    parser_set_skill.add_argument('skill_name', help='Skill name, e.g. "craft". Run `show skills` to see all skill names.')
    parser_set_skill.add_argument('skill_level', type = int, help='''Desired skill level. 
                        Skill will only update if enough points are available and skill is not already at or above this level.''')
    parser_set_skill.add_argument('summoner_ids', help='''One or more summoner ids whose skills to adjust. 
                        Can also be "all", in which case all summoners on the address will change skills.''', nargs="+")
                    

    # Command CRAFT
    parser_craft = subparsers.add_parser("craft", parents=[shared_parser],
                        help = "Craft items")
    parser_craft.add_argument('base_type', help='What type of item.', 
                        choices = ["good", "armor", "weapon"])
    parser_craft.add_argument("item_id", help='Which item to craft (integer)', type = int)
    parser_craft.add_argument('--crafter', help = "Summoner ID of the crafter", required = True, type = int)
    parser_craft.add_argument('--mats', help = "Amount of crafting material to use", required = True, type = int)
    parser_craft.add_argument('-n', '--amount', help = "Number of items to create (default = 1)", default = 1, type = int)
    parser_craft.add_argument('--simulate', help = "Simulate craft", action = "store_true")

    # Command SETUP-CRAFTING
    parser_setup_crafting = subparsers.add_parser("setup-crafting", parents=[shared_parser],
                        help = '''Setup approvals so your summoners can craft. 
                        Note this does not set up attributes or skills, see set-attributes and set-skills for that.''')
    parser_setup_crafting.add_argument('summoner_ids', help='''One or more summoner ids to setup for crafting. 
                        Can also be "all", in which case all summoners on the address will be ready to craft.''', nargs="+")
    parser_setup_crafting.add_argument('--approve-for-all', help='''Recommended. If enabled, the bot will use setApprovalForAll() 
                        rather than approve() to enable the crafting contract to spend your XP. This is much more efficient as
                        only one tx is needed to approve for all the summoners, and the approval will be permanent (until revoked).
                        However, this gives more permissions than strictly needed to the crafting contract.''',
                        action = "store_true")
                               

    return parser