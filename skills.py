from raritydata import RarityData
from colorama.ansi import Fore
from tabulate import tabulate
from web3.main import Web3

from transacter import Transacter

class InvalidSkillError(Exception):
    pass

class SkillCodex:

    contract_addresses = {
        "skill_codex": "0x67ae39a2Ee91D7258a86CD901B17527e19E493B3",
        "skills": "0x6292f3fB422e393342f257857e744d43b1Ae7e70"
    }

    codex_sizes = {
        "skill_codex": 36
    }

    # Contracts adress checksums
    contract_checksums = {k: Web3.toChecksumAddress(v) for k, v in contract_addresses.items()}

    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider('https://rpc.ftm.tools/'))
        self.contracts = {cname: Transacter.rate_limit(self.get_codex_contract(cname)) for cname in self.contract_addresses.keys()}
        self.class_skills = {class_id: self.get_class_skills(class_id) for class_id in range(1,12)}

    def get_codex_contract(self, codex_name):
        '''Get contract or raise a KeyError if contract isn't listed'''
        return self.w3.eth.contract(address = self.contract_checksums[codex_name], 
                            abi = Transacter.get_abi(self.contract_addresses[codex_name]))

    def get_class_skills(self, class_id):
        return self.contracts["skills"].functions.class_skills_by_name(class_id).call()

    def get_classes(self, skill_name):
        class_ids = [class_id for class_id in self.class_skills if skill_name in self.class_skills[class_id]]
        return [RarityData.class_names[class_id] for class_id in class_ids]

    def get_skill_data(self, id):
        if id > self.codex_sizes["skill_codex"]:
            raise InvalidSkillError("Invalid skill id")
        item_data = self.contracts["skill_codex"].functions.skill_by_id(id).call()
        return item_data

    def get_skills(self):
        num_skills = self.codex_sizes["skill_codex"]
        return [Skill(id, self) for id in range(1, num_skills + 1)]

    def get_skill_name(self, id):
        return self.get_skill_data(id)[1]

    def get_skill_names(self):
        num_skills = self.codex_sizes["skill_codex"]
        return [self.get_skill_name(id) for id in range(1, num_skills + 1)]

    def get_skill_id(self, skill_name):
        """Get skill ID from skill name (case-insensitive)"""
        skill_names_lower = [s.lower() for s in RarityData.skill_names]
        try:
            skill_id = skill_names_lower.index(skill_name.lower()) + 1
        except ValueError:
            raise InvalidSkillError("Not a valid skill")
        return skill_id

class Skill:

    def __init__(self, id, codex):
        id, name, attr_id, synergy, retry, armor_check_penalty, check, action = codex.get_skill_data(id)
        self.skill_id = id
        self.name = name
        self.attribute_id = attr_id
        self.attribute = ["str", "dex", "const", "int", "wis", "cha"][attr_id - 1]
        self.synergy = synergy
        self.retry = retry
        self.armor_check_penalty = armor_check_penalty
        self.check = check
        self.action = action
        self.classes = codex.get_classes(self.name)

    def __str__(self):
        return f"Skill {self.name}"

    def get_details(self):
        return {
            "id": self.skill_id,
            "name": self.name,
            "attribute": self.attribute,
            "classes": ', '.join(self.classes),
            "synergy": self.synergy,
            "retry": self.retry,
            "armor_check_penalty": self.armor_check_penalty
        }

    @staticmethod
    def print_skills(skills):
        def print_tbl(dict):
            print(Fore.WHITE + tabulate(dict, headers = "keys", tablefmt = "pretty"))

        # Text doesn't fit in a table so we print line by line
        for skill in skills:
            print(f"Skill #{skill.skill_id}: {skill.name} ----------------")
            print("Check: " + skill.check)
            print("Action: " + skill.action + "\n")

        print("------- Skill metadata ---------")
        skill_data = [skill.get_details() for skill in skills]
        print_tbl(skill_data)
