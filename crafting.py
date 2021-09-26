from colorama.ansi import Fore
from tabulate import tabulate
from transacter import Transacter
from web3.main import Web3


class CraftingEngine:

    contract_addresses = {
        "crafting": "0xf41270836dF4Db1D28F7fd0935270e3A603e78cC"
    }

    # Contracts adress checksums
    contract_checksums = {k: Web3.toChecksumAddress(v) for k, v in contract_addresses.items()}

    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider('https://rpc.ftm.tools/'))
        self.contracts = {cname: Transacter.rate_limit(self.get_codex_contract(cname)) for cname in self.contract_addresses.keys()}

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