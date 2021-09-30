from colorama.ansi import Fore
from tabulate import tabulate
from transacter import Transacter
from web3.main import Web3

class CraftingError(Exception):
    pass

class CraftingEngine:

    contract_addresses = {
        "crafting": "0xf41270836dF4Db1D28F7fd0935270e3A603e78cC"
    }

    # This is the summoner owned by the crafting contract who spends your gold and craft mats when you craft
    crafting_spender = 1758709

    # Contracts adress checksums
    contract_checksums = {k: Web3.toChecksumAddress(v) for k, v in contract_addresses.items()}

    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider('https://rpc.ftm.tools/'))
        self.contracts = {cname: Transacter.rate_limit(self.get_contract(cname)) for cname in self.contract_addresses.keys()}

    def get_contract(self, contract_name):
        '''Get contract or raise a KeyError if contract isn't listed'''
        return self.w3.eth.contract(address = self.contract_checksums[contract_name], 
                                    abi = Transacter.get_abi(self.contract_addresses[contract_name]))

    @staticmethod
    def check_craft_proba(craft_level, int_level, item_dc, craft_mats):
        if craft_level == 0:
            return 0
        int_modifier = (int_level - 10) // 2
        if craft_level + int_modifier <= 0:
            return 0
        item_dc = max(item_dc - craft_mats // 10, 0)
        check = craft_level + int_modifier - item_dc
        check_plus_d20 = [check + d20 for d20 in range(0, 20)]
        proba = sum([x >= 0 for x in check_plus_d20]) / 20
        return proba

    @staticmethod
    def check_craft(summoner, item, craft_mats):
        return CraftingEngine.check_craft_proba(summoner.get_craft_level(), summoner.attributes["int"], item.DC, craft_mats)

    @staticmethod
    def get_proba_data(item_dc):
        data = []

        for int_level in range(18, 25, 2):
            for craft_level in range(4, 8):
                for craft_mats in range(0, 500, 10):
                    proba = CraftingEngine.check_craft_proba(craft_level, int_level, item_dc, craft_mats)
                    if proba >= 0.7:
                        data.append({
                            "Item DC": item_dc,
                            "Intelligence": int_level,
                            "Craft Level": craft_level,
                            "Crafting Material Spent": craft_mats,
                            "Probability of Success": str(round(100 * proba, 2)) + "%"
                        })
                    if proba == 1:
                        break
        return data

    @staticmethod
    def print_proba_table(item_dc):
        tbl = tabulate(CraftingEngine.get_proba_data(item_dc), headers = "keys", tablefmt = "pretty")
        print(Fore.WHITE + tbl)

    def simulate(self, summoner, item, craft_mats, times = 1):
        """Simulate item crafting (proba + repeated attempts)"""
        # 1. Show proba
        print(f"Simulating craft of a {item} with {summoner} using {craft_mats} crafting material:")
        proba = CraftingEngine.check_craft(summoner, item, craft_mats)
        print(f"Success probability: {round(100 * proba, 1)}%")

        # 2. Actual attempts
        if times:
            print(f"Simulating using crafting contract:")
            attempts = [Transacter.rate_limit(self._simulate(summoner.token_id, item.base_type_id, item.item_id, craft_mats), 4) \
                        for _ in range(times)]
            
            success_rate = sum(attempts) / times
            print(f"Success rate: {round(100 * success_rate, 1)}%")
        return proba
        

    def _simulate(self, summoner_id, base_type, item_type, craft_mats):
        """Call simulate() from the crafting contract"""
        crafted, check, cost, dc = self.contracts["crafting"].functions.\
            simulate(summoner_id, base_type, item_type, craft_mats).call()
        cost = cost / 1e18
        if crafted:
            print(Fore.GREEN + f"Success!\tCheck: {check}\tItem DC:{dc} \tCost:{cost}" + Fore.RESET)
        else:
            print(Fore.RED + f"Failure!\tCheck: {check}\tItem DC:{dc} \tCost:{cost}" + Fore.RESET)
        return crafted

    def craft(self, summoner, item, craft_mats):
        if not summoner.signer:
            raise CraftingError("Summoner can't sign tx without a signer")
        if summoner.gold < item.cost:
            raise CraftingError("Summoner doesn't have enough gold to craft the item")
        if craft_mats < 0 or craft_mats % 10 != 0:
            raise CraftingError("Invalid quantity of crafting material (should be a multiple of 10)")
        if summoner.get_balance_craft1() < craft_mats:
            raise CraftingError("Summoner doesn't have enough crafting material")
        if summoner.get_craft_level() == 0:
            raise CraftingError("Summoner can't craft. Increase crafting skill level.")
        
        success_proba = self.check_craft(summoner, item, craft_mats)
        if success_proba == 0:
            raise CraftingError("Summoner has no chance to craft this: aborting")
        if success_proba < 0.5:
            raise CraftingError(f"Success proba is too low ({round(100 * success_proba, 1)}%): aborting")

        print(f"Attempting to craft a {item} with {summoner}. Success probability: {round(100 * success_proba, 1)}%")
        craft_fun = self.contracts["crafting"].functions.craft(summoner.token_id, item.base_type_id, item.item_id, craft_mats)
        return summoner.sign_and_execute(craft_fun, gas = 500000)
        
    @staticmethod
    def setup_crafting(summoner, approve_for_all = False):
        """Set up approvals required before crafting"""
        tx1 = tx2 = tx3 = None

        # Approving the crafting contract on the summoner (required so it can spend XP)
        crafting_contract = CraftingEngine.contract_addresses["crafting"]
        if not summoner.is_approved(crafting_contract):
            if approve_for_all:
                tx1 = summoner.approve_for_all(crafting_contract)
                if tx1["status"] == "pending":
                    # Force to wait so we don't approve_for_all more than once by mistake
                    tx1["receipt"] = summoner.transacter.wait_for_receipt(tx1["hash"])
            else:
                tx1 = summoner.approve(crafting_contract)

        # The crafting contract owns  summoner who spends your gold and craft mats when you craft
        crafting_spender = CraftingEngine.crafting_spender
        if summoner.get_gold_allowance(crafting_spender) == 0:
            tx2 = summoner.approve_gold(crafting_spender)
        if summoner.get_craft_mats_allowance(crafting_spender) == 0:
            tx3 = summoner.approve_craft_mats(crafting_spender)

        return tx1, tx2, tx3

    @staticmethod
    def is_ready_to_craft(summoner):
        crafting_contract = CraftingEngine.contract_addresses["crafting"]
        crafting_spender = CraftingEngine.crafting_spender
        return  summoner.get_craft_level() > 0 and \
                summoner.is_approved(crafting_contract) and \
                summoner.get_gold_allowance(crafting_spender) > 0 and \
                summoner.get_craft_mats_allowance(crafting_spender) > 0