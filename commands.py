from summoner import InvalidAmountError, InvalidSummonerError, Summoner
from list_summoners import list_items, list_summoners
from summoning import SummoningEngine
from colorama import Fore
import key

def command_show(args, transacter):
    if args.what == "summoners":
        # Listing summoners
        list_summoners(transacter.address, transacter, verbose = True)
    elif args.what == "gas": 
        # Printing gas price and action costs
        transacter.print_gas_price()
    elif args.what == "items":
        # Listing crafted items
        list_items(transacter.address, verbose = True)
        

def command_summon(args, transacter):
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

def command_run(args, transacter):
    print_list = "list" in args.actions
    summoners = list_summoners(transacter.address, transacter, verbose = print_list)
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

def command_transfer(args, transacter, transfer_all = False):
    if not args.from_id:
        raise InvalidSummonerError("Must specify a sender with `--from`")
    
    summoners = list_summoners(transacter.address, transacter, verbose = False)
    summoner_ids = [str(round(s.token_id)) for s in summoners]
    
    # Set sender(s)
    if args.from_id == "all":
        senders = summoners
    elif args.from_id not in summoner_ids:
        print(summoner_ids)
        raise InvalidSummonerError("Sender (" + args.from_id + ") is not owned by this address.")
    else:
        try:
            sender_id = int(args.from_id)
        except ValueError:
            raise InvalidSummonerError("Invalid sender ID")
        senders = [Summoner(sender_id, transacter)]

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

