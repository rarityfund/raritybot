from colorama.ansi import Fore
from tabulate import tabulate
from web3.main import Web3

from summoner import InvalidAddressError
from transacter import Transacter


class InvalidItemError(Exception):
    pass

class Codex:

    contract_addresses = {
        "goods": "0x0C5C1CC0A7AE65FE372fbb08FF16578De4b980f3",
        "armors": "0xf5114A952Aca3e9055a52a87938efefc8BB7878C",
        "weapons": "0xeE1a2EA55945223404d73C0BbE57f540BBAAD0D8",
        "crafting": "0xf41270836dF4Db1D28F7fd0935270e3A603e78cC"
    }

    codex_sizes = {
        "goods": 24,
        "armors": 18,
        "weapons": 59
    }

    # Contracts adress checksums
    contract_checksums = {k: Web3.toChecksumAddress(v) for k, v in contract_addresses.items()}

    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider('https://rpc.ftm.tools/'))
        self.contracts = {cname: Transacter.rate_limit(self.get_codex_contract(cname)) for cname in self.contract_addresses.keys()}

    def get_codex_contract(self, codex_name):
        '''Get contract or raise a KeyError if contract isn't listed'''
        return self.w3.eth.contract(address = self.contract_checksums[codex_name], 
                            abi = Transacter.get_abi(self.contract_addresses[codex_name]))

    def get_item_data(self, codex_name, id):
        try:
            contract = self.contracts[codex_name]
            size = self.codex_sizes[codex_name]
        except KeyError:
            raise InvalidItemError("Invalid codex name")
        if id > size:
            raise InvalidItemError("Invalid item id: too big")
        item_data = contract.functions.item_by_id(id).call()
        return item_data

    def get_items(self, codex_name):
        try:
            contract = self.contracts[codex_name]
            size = self.codex_sizes[codex_name]
        except KeyError:
            raise InvalidItemError("Invalid codex name")
        return [Item.create_from_data(codex_name, id, self) for id in range(1, size+1)]
        
class Item:

    base_type_from_id = {
        1: "goods",
        2: "armors",
        3: "weapons"
    }

    @classmethod
    def create_from_data(cls, base_type, item_id, codex):
        class_mapping = {
            "goods": Good,
            "weapons": Weapon,
            "armors": Armor
        }
        item_data = codex.get_item_data(base_type, item_id)
        item_class = class_mapping[base_type]
        return item_class(item_data)

    @classmethod
    def create_from_token(cls, token_id, codex):
        (base_type, item_type, crafted, crafter) = codex.contracts["crafting"].functions.items(token_id).call()
        return Item.create_from_data(cls.base_type_from_id[base_type], item_id = item_type, codex = codex)

    def __init__(self):
        raise InvalidItemError("Items must be instantiated with Item.create_from_data or Item.create_from_token")

    def __str__(self):
        return f"{self.name} ({self.base_type} #{self.item_id})"

    @staticmethod
    def print_items(items):
        details = [item.get_details() for item in items]
        tbl = tabulate(details, headers = "keys", tablefmt = "fancy")
        print(Fore.WHITE + tbl)


class Good(Item):

    base_type = "goods"

    def __init__(self, item_data):
        self.parse_item_data(item_data)

    def parse_item_data(self, item_data):
        (item_id, cost, weight, name, description) = item_data
        self.item_id = item_id
        self.cost = cost / 1e18
        self.weight = weight
        self.name = name
        self.desciption = description

    def get_details(self):
        return {
            "base_type": self.base_type,
            "item_id": self.item_id,
            "name": self.name,
            "cost": self.cost,
            "weight": self.weight
        }

class Weapon(Item):

    base_type = "weapons"

    proficiency_by_id = {
        1: "Simple",
        2: "Martial",
        3: "Exotic"
    }

    encumbrance_by_id = {
            1: "Unarmed",
            2: "Light Melee Weapons",
            3: "One-Handed Melee Weapons",
            4: "Two-Handed Melee Weapons",
            5: "Ranged Weapons",
    }
    
    damage_type_by_id = {
        1: "Bludgeoning",
        2: "Piercing",
        3: "Slashing"
    }

    def __init__(self, item_data):
        self.parse_item_data(item_data)
    
    def parse_item_data(self, item_data):
        (item_id, cost, proficiency, encumbrance, damage_type, weight, damage, critical, critical_modifier, range_increment, name, description) = item_data
        self.item_id = item_id
        self.cost = cost / 1e18
        self.weight = weight
        self.proficiency = proficiency
        self.encumbrance = encumbrance
        self.damage = damage
        self.damage_type = damage_type
        self.critical = critical
        self.critical_modifier = critical_modifier
        self.range_increment = range_increment
        self.name = name
        self.description = description

    def get_details(self):
        return {
            "base_type": self.base_type,
            "item_id": self.item_id,
            "name": self.name,
            "cost": self.cost,
            "weight": self.weight,
            "encumbrance": self.encumbrance_by_id[self.encumbrance],
            "proficiency": self.proficiency_by_id[self.proficiency],
            "damage (type)": f"{self.damage} ({self.damage_type_by_id[self.damage_type]})",
            "critical (crit mod)": str(self.critical) + (f" ({self.critical_modifier})" if self.critical_modifier else ''),
            "range_increment": self.range_increment
        }

class Armor(Item):

    base_type = "armors"

    proficiency_by_id = {
        1: "Light",
        2: "Medium",
        3: "Heavy",
        4: "Shield"
    }

    def __init__(self, item_data):
        self.parse_item_data(item_data)

    
    def parse_item_data(self, item_data):
        (item_id, cost, proficiency, weight, armor_bonus, max_dex_bonus, penalty, spell_failure, name, description) = item_data
        self.item_id   = item_id
        self.cost = cost / 1e18
        self.proficiency = proficiency
        self.weight = weight
        self.armor_bonus = armor_bonus
        self.max_dex_bonus = max_dex_bonus
        self.penalty = penalty
        self.spell_failure = spell_failure
        self.name = name
        self.description = description

    def get_details(self):
        return {
            "base_type": self.base_type,
            "item_id": self.item_id,
            "name": self.name,
            "cost": self.cost,
            "weight": self.weight,
            "proficiency": self.proficiency_by_id[self.proficiency],
            "armor_bonus": self.armor_bonus,
            "max_dex_bonus": self.max_dex_bonus,
            "penalty": self.penalty,
            "spell_failure": self.spell_failure
        }
