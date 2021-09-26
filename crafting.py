
from logging import critical
from summoner import InvalidAddressError
from web3.main import Web3
from transacter import Transacter

class InvalidItemError(Exception):
    pass

class Codex:

    codex_addresses = {
        "goods": "0x0C5C1CC0A7AE65FE372fbb08FF16578De4b980f3",
        "armors": "0xf5114A952Aca3e9055a52a87938efefc8BB7878C",
        "weapons": "0xeE1a2EA55945223404d73C0BbE57f540BBAAD0D8"
    }

    codex_sizes = {
        "goods": 24,
        "armors": 18,
        "weapons": 59
    }

    # Contracts adress checksums
    codex_checksums = {k: Web3.toChecksumAddress(v) for k, v in codex_addresses.items()}

    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider('https://rpc.ftm.tools/'))
        self.codex_contracts = {cname: Transacter.rate_limit(self.get_codex_contract(cname)) for cname in self.codex_addresses.keys()}

    def get_codex_contract(self, codex_name):
        '''Get contract or raise a KeyError if contract isn't listed'''
        return self.w3.eth.contract(address = self.codex_checksums[codex_name], 
                            abi = Transacter.get_abi(self.codex_addresses[codex_name]))

    def get_item_data(self, codex_name, id):
        try:
            contract = self.codex_contracts[codex_name]
            size = self.codex_sizes[codex_name]
        except KeyError:
            raise InvalidItemError("Invalid codex name")
        if id > size:
            raise InvalidItemError("Invalid item id: too big")
        item_data = contract.functions.item_by_id(id).call()
        return item_data

    def get_items(self, codex_name):
        try:
            contract = self.codex_contracts[codex_name]
            size = self.codex_sizes[codex_name]
        except KeyError:
            raise InvalidItemError("Invalid codex name")
        return [Item.create(codex_name, id, self) for id in range(1, size+1)]

        
class Item:

    base_types = {
        "1": "goods",
        "2": "armors",
        "3": "weapons"
    }


    def create(base_type, item_id, codex):
        if base_type in ["good", "goods"]:
            item_data = codex.get_item_data("goods", item_id)
            return Good(item_data)
        elif base_type in ["armor", "armors"]:
            item_data = codex.get_item_data("armors", item_id)
            return Armor(item_data)
        elif base_type in ["weapon", "weapons"]:
            item_data = codex.get_item_data("weapons", item_id)
            return Weapon(item_data)
        else:
            raise InvalidItemError("Invalid base_type")

    def __init__(self):
        raise InvalidItemError("Items must be instantiated with Item.create() or Good() / Armor() / Weapon()")

    def __str__(self):
        return f"{self.name} ({self.base_type} #{self.item_id})"

class Good(Item):

    def __init__(self, item_data):
        self.base_type = "good"
        self.parse_item_data(item_data)

    def parse_item_data(self, item_data):
        (item_id, cost, weight, name, description) = item_data
        self.item_id = item_id
        self.cost = cost
        self.weight = weight
        self.name = name
        self.desciption = description

class Weapon(Item):

    def __init__(self, item_data):
        self.base_type = "weapon"
        self.parse_item_data(item_data)
    
    def parse_item_data(self, item_data):
        (item_id, cost, proficiency, encumbrance, damage_type, weight, damage, critical, critical_modifier, range_increment, name, description) = item_data
        self.item_id = item_id
        self.cost = cost,
        self.proficiency = proficiency
        self.encumbrance = encumbrance
        self.damage_type = damage_type
        self.weight = weight
        self.damage = damage
        self.critical = critical_modifier,
        self.range_increment = range_increment,
        self.name = name
        self.description = description


class Armor(Item):

    def __init__(self, item_data):
        self.base_type = "armor"
        self.parse_item_data(item_data)

    
    def parse_item_data(self, item_data):
        (item_id, cost, proficiency, weight, armor_bonus, max_dex_bonus, penalty, spell_failure, name, description) = item_data
        self.item_id   = item_id
        self.cost = cost,
        self.proficiency = proficiency
        self.weight = weight
        self.armor_bonus = armor_bonus,
        self.max_dex_bonus = max_dex_bonus
        self.penalty = penalty
        self.spell_failure = spell_failure
        self.name = name
        self.description = description