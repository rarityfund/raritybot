from skills import InvalidSkillError, Skill, SkillCodex
from crafting import CraftingEngine, CraftingError
from items import ItemCodex, Item
from rarity import get_address_from_args, get_signer_from_args, print_intro
from summoner import InvalidAddressError, InvalidAmountError, InvalidSummonerError, Summoner
from list_summoners import list_items, list_summoners
from summoning import SummoningError, SummoningEngine
from colorama import Fore
from key import InvalidInputError

def command_show(args, transacter):
    if args.what == "summoners":
        # Listing summoners
        owner_address = get_address_from_args(args)
        summoners = list_summoners(owner_address, transacter, limit = args.limit)
        Summoner.print_summoners(summoners)

    elif args.what == "gas": 
        # Printing gas price and action costs
        transacter.print_gas_price()

    elif args.what == "skills":
        codex = SkillCodex()
        Skill.print_skills(codex.get_skills())
    
    elif args.what == "items":
        # Listing crafted items
        owner_address = get_address_from_args(args)
        items = list_items(owner_address, limit = args.limit)
        Item.print_items(items)
    
    elif args.what == "craftable":
        codex = ItemCodex()
        Item.print_items(codex.get_items("goods"))
        Item.print_items(codex.get_items("weapons"))
        Item.print_items(codex.get_items("armors"))

    elif args.what == "crafting-proba":
        item_dc = args.limit if args.limit else 20
        print("Probability table when crafting items with DC=" + str(item_dc))
        CraftingEngine.print_proba_table(item_dc = item_dc)

def command_summon(args, transacter):
    # Summoning new summoners
    signer = get_signer_from_args(args)
    summoning_engine = SummoningEngine(transacter, signer = signer)

    # Parse attributes if provided
    summoning_attributes = None
    if args.attributes:
        try:
            summoning_attributes = summoning_engine.parse_attributes(args.attributes)
        except InvalidInputError as e:
            print(Fore.RED + str(e) + Fore.RESET)
            exit()

    if not args.summoner_class:
        # Class must be provided
        print("Error: need class to summon. Pass it with `--class`.")

    elif args.txmode == "batch":
        # In batch mode, we won't have the summoner ids until we get the receipts at the end
        for i in range(args.count):
            print(Fore.WHITE + "Creating new summoner of class " + str(args.summoner_class))
            try:
                summoning_engine.summon_from_class(args.summoner_class)
            except SummoningError as e:
                print(Fore.RED + str(e) + Fore.RESET)
        receipts = transacter.wait_for_pending_transations()
        print(Fore.YELLOW + "Created " + str(len(receipts)) + " summoner" + ("s" if len(receipts) > 1 else "") + ":")
        summoner_ids = []
        for receipt in receipts:
            summon_details = summoning_engine.get_details_from_summon_receipt(receipt)
            if summon_details:
                print(Summoner(summon_details["token_id"], transacter))
                summoner_ids.append(summon_details["token_id"])
            else:
                print(Fore.RED + "Could not get summon data - CANNOT ASSIGN ATTRIBUTES")
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
            try:
                new_id = summoning_engine.summon_from_class(args.summoner_class)
                summoner_ids.append(new_id)
                summoning_engine.set_attributes(new_id, summoning_attributes)
            except (InvalidInputError, SummoningError) as e:
                print(Fore.RED + str(e) + Fore.RESET)
        print(Fore.YELLOW + "Created " + str(len(summoner_ids)) + " summoner" + \
                ("s" if len(summoner_ids) > 1 else "") + ":")
        
        for token_id in summoner_ids:
            print(Summoner(token_id, transacter))

def command_run(args, transacter):
    owner_address = get_address_from_args(args)
    signer = get_signer_from_args(args)
    summoners = list_summoners(owner_address, transacter, set_signer = signer)

    if "list" in args.actions:
        Summoner.print_summoners(summoners)
        print("\n")

    if not summoners:
        print("This address doesn't contains any rarities, bot is exiting..." + Fore.RESET)
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

def command_transfer(args, transacter, transfer_all = False):
    if not args.from_id:
        raise InvalidSummonerError("Must specify a sender with `--from`")
    
    owner_address = get_address_from_args(args)
    signer = get_signer_from_args(args)
    summoners = list_summoners(owner_address, transacter, set_signer = signer)
    summoner_ids = [str(round(s.token_id)) for s in summoners]
    
    # Set sender(s)
    if args.from_id == "all":
        senders = summoners
    elif args.from_id not in summoner_ids:
        raise InvalidSummonerError("Sender (" + args.from_id + ") is not owned by this address.")
    else:
        try:
            sender_id = int(args.from_id)
        except ValueError:
            raise InvalidSummonerError("Invalid sender ID")
        senders = [Summoner(sender_id, transacter, signer = signer)]

    # Check recipient
    if args.to_id not in summoner_ids and not args.force:
        raise InvalidSummonerError("Recipient (" + args.to_id + ") is not owned by this address. " + \
                                   "Use `--force` to authorise this transfer.")
    try:
        recipient_id = int(args.to_id)
    except ValueError:
        raise InvalidSummonerError("Invalid recipient ID")
    
    # Set amount
    amount = "max" if transfer_all else args.amount
    
    # Do the transfer(s)
    for sender in senders:
        if args.what == "gold":
            sender.transfer_gold(recipient_id, amount = amount)
        elif args.what == "craft1":
            sender.transfer_craft1(recipient_id, amount = amount)
        else:
            raise InvalidAmountError("Invalid token: cannot transfer")

    transacter.wait_for_pending_transations()


def command_send_summoner(args, transacter):
    if not args.who:
        raise InvalidSummonerError("Must specify who to send.")
    
    owner_address = get_address_from_args(args)
    signer = get_signer_from_args(args)
    summoners = list_summoners(owner_address, transacter, set_signer = signer)
    summoner_ids = [str(round(s.token_id)) for s in summoners]
    
    # Set sender(s)
    if args.who == "all":
        if not args.force:
            print("Warning: you are about to send ALL your summoners! Use `--force` to force the transfer.")
            return None
        senders = summoners
    elif args.who not in summoner_ids:
        raise InvalidSummonerError("Summoner (" + args.who + ") is not owned by this address.")
    else:
        try:
            sender_id = int(args.who)
        except ValueError:
            raise InvalidSummonerError("Invalid sender ID")
        senders = [Summoner(sender_id, transacter, signer = signer)]

    # Check recipient
    if not args.to_address:
        raise InvalidAddressError("Must provide an address with `--to`")
    
    # Do the transfer(s)
    for sender in senders:
        try:
            sender.transfer_to_new_owner(args.to_address)
        except InvalidAddressError as e:
            print(e)

    transacter.wait_for_pending_transations()

def command_setup_crafting(args, transacter):
    owner_address = get_address_from_args(args)
    signer = get_signer_from_args(args)

    # Preparing summoners
    if len(args.summoner_ids) == 1 and args.summoner_ids[0] == "all":
        summoners = list_summoners(owner_address, transacter, set_signer = signer)
    else:
        summoners = [Summoner(id, transacter, signer = signer) for id in args.summoner_ids]

    if (args.approve_for_all):
        print(Fore.YELLOW + "Setting up crafting with --approve-for-all. This will:")
        print(f"- Approve the crafting contract ({CraftingEngine.contract_addresses['crafting']}) on your address")
        print("Then, for each selected summoner:")
        print(f"- approve gold spending for summoner {CraftingEngine.crafting_spender} (owned by the crafting contract)")
        print(f"- approve craft mats spending for summoner {CraftingEngine.crafting_spender} (owned by the crafting contract)")
        print(Fore.RESET)
    else:
        print(Fore.YELLOW + "Setting up crafting without --approve-for-all. For each selected summoner, this will:")
        print(f"- Approve the crafting contract ({CraftingEngine.contract_addresses['crafting']}) for that particular summoner")
        print(f"- approve gold spending by summoner {CraftingEngine.crafting_spender} (owned by the crafting contract)")
        print(f"- approve craft mats spending by summoner {CraftingEngine.crafting_spender} (owned by the crafting contract)")
        print(Fore.RESET)
        
    # Setting approvals as required
    for summoner in summoners:
        summoner.prepare_to_craft(approve_for_all = args.approve_for_all)

    transacter.wait_for_pending_transations()

def command_craft(args, transacter):
    args.base_type = args.base_type + "s"
    codex = ItemCodex()
    item = Item.create_from_data(args.base_type, args.item_id, codex = codex)
    summoner = Summoner(args.crafter, transacter = transacter)
    crafting_engine = CraftingEngine()

    if args.simulate:
        crafting_engine.simulate(summoner, item, args.mats, times = args.amount)
    else:
        signer = get_signer_from_args(args)
        summoner.set_signer(signer)
        receipts = []
        for _ in range(args.amount):
            try:
                tx_status = crafting_engine.craft(summoner, item, args.mats)
                if tx_status["status"] == "pending":
                    receipts.extend(transacter.wait_for_pending_transations())
                else:
                    receipts.append(tx_status["receipt"])
            except CraftingError as e:
                print(Fore.RED + str(e) + Fore.RESET)
                break
        print(receipts)

def command_set_attributes(args, transacter):
    owner_address = get_address_from_args(args)
    signer = get_signer_from_args(args)

    summoning_engine = SummoningEngine(transacter, signer)

    # Parse and check attributes
    try:
        attributes = summoning_engine.parse_attributes(args.attributes)
    except InvalidInputError as e:
        print(Fore.RED + str(e) + Fore.RESET)
        exit()

    # Preparing summoners
    if len(args.summoner_ids) == 1 and args.summoner_ids[0] == "all":
        summoners = list_summoners(owner_address, transacter, set_signer = signer)
    else:
        summoners = [Summoner(id, transacter, signer = signer) for id in args.summoner_ids]

    # Assigning Attributes
    for summoner in summoners:
        try:
            summoner.set_attributes(attributes)
        except (InvalidInputError, PermissionError, InvalidSummonerError) as e:
            print(Fore.RED + str(e) + Fore.RESET)

    transacter.wait_for_pending_transations()


def command_set_skill(args, transacter):
    owner_address = get_address_from_args(args)
    signer = get_signer_from_args(args)
    
    # Check skill name is valid
    codex = SkillCodex()
    try:
        codex.get_skill_id(args.skill_name)
    except InvalidSkillError as e:
        print(e)
        return None

    # Preparing summoners
    if len(args.summoner_ids) == 1 and args.summoner_ids[0] == "all":
        summoners = list_summoners(owner_address, transacter, set_signer = signer)
    else:
        summoners = [Summoner(id, transacter, signer = signer) for id in args.summoner_ids]

    # Assigning skills
    for summoner in summoners:
        try:
            summoner.set_skill(args.skill_name, args.skill_level)
        except (InvalidSummonerError, InvalidSkillError) as e:
            print(Fore.RED + str(e) + Fore.RESET)

    transacter.wait_for_pending_transations()