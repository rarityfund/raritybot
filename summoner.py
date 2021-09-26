from colorama import Fore
from web3.main import Web3

class InvalidSummonerError(Exception):
    """Used to indicate an invalid summoner is handled"""
    pass

class InvalidAmountError(Exception):
    """Used to indicate invalid amounts during transfers"""
    pass

class InvalidAddressError(Exception):
    """Used to indicate invalid addresses"""
    pass

class Summoner:
    '''Fetch summoner details and handle summoner actions'''

    classes =  ["No class",
                "Barbarian",
                "Bard",
                "Cleric",
                "Druid",
                "Fighter",
                "Monk",
                "Paladin",
                "Ranger",
                "Rogue",
                "Sorcerer",
                "Wizard"]

    def __init__(self, id, transacter, signer = None):
        # What we need to transact
        self.transacter = transacter
        self.signer = signer
        self.contracts = transacter.contracts
        self.token_id = id
        self.update_summoner_info()
        self.update_gold_balance()

    def __str__(self):
        return "A " + self.class_name + " (" + str(self.token_id) + ")"

    def set_signer(self, signer):
        self.signer = signer

    def get_details(self):
        """Get a dict full of details about the summoner.
           Print it with tabulate for best results."""
        xp_str = str(round(self.xp)) + "/" + str(round(self.xp_required()))
        return  {
            "SummonerId": self.token_id,
            "Class": self.class_name,
            "Level": "lvl " + str(self.level),
            "XP": xp_str,
            "Gold": round(self.gold),
            "Craft Mat(I)": round(self.get_balance_craft1()),
            "Next Adventure": self.seconds_to_hms(self.time_to_next_adventure()),
            "Next Cellar": self.seconds_to_hms(self.time_to_next_cellar()),
            "Cellar Loot": round(self.expected_cellar_loot())
        }
                
    @staticmethod
    def seconds_to_hms(secs):
        if (secs <= 0):
            return "READY".rjust(9, ' ')
        h = secs // 3600
        secs = secs % 3600
        m = secs // 60
        s = secs % 60
        hms = str(h) + "h" + str(m) + "m" + str(s) + "s"
        return hms.rjust(9, ' ')
    
    def update_summoner_info(self):
        """Update class, level and xp"""
        summoner_info = self.contracts["summoner"].functions.summoner(self.token_id).call()
        self.class_id = summoner_info[2]
        self.class_name = self.class_from_index(summoner_info[2])
        self.level =  summoner_info[3]
        self.xp = summoner_info[0] / 1e18

    @classmethod
    def class_from_index(cls, index):
        '''Get class from index (local lookup)'''
        try:
          return cls.classes[index]
        except IndexError:
            print("Invalid class ID")
            return "N/A"

    ### GOLD -----------------------------

    def update_gold_balance(self):
        self.gold = self.get_balance_gold()

    def check_claim_gold(self):
        claimable_gold = self.contracts["gold"].functions.claimable(self.token_id).call()
        return claimable_gold > 0

    def claim_gold(self):
        if self.check_claim_gold():
            print(Fore.WHITE + str(self) + " is claiming gold")
            claim_gold_fun = self.contracts["gold"].functions.claim(self.token_id)
            tx_status = self.transacter.sign_and_execute(claim_gold_fun, gas = 120000, signer = self.signer)
            if tx_status["status"] == "success":
                print("The summoner claimed gold with success !")
                self.update_gold_balance()

    def get_balance_gold(self):
        return self.get_balance_erc20(self.transacter.contracts["gold"], scaling_factor = 1e18)

    def transfer_gold(self, to_id, amount):
        print(Fore.WHITE + "Sending " + str(amount) + " gold from " + str(self.token_id) + " to " + str(to_id))
        return self.transfer_erc20(to_id, amount, contract = self.contracts["gold"], scaling_factor = 1e18)


    ### ADVENTURE ------------------------

    def time_to_next_adventure(self):
        """Get time to next adventure in seconds"""
        next_time_available = self.contracts["summoner"].functions.adventurers_log(self.token_id).call()
        current_time = self.transacter.timestamp
        return next_time_available - current_time

    def check_adventure(self):    
        return self.time_to_next_adventure() <= 0

    def adventure(self):
        if self.check_adventure():
            print(Fore.WHITE + str(self) + " has gone on an adventure!")
            adventure_fun = self.contracts["summoner"].functions.adventure(self.token_id)
            tx_status = self.transacter.sign_and_execute(adventure_fun, gas = 70000, signer = self.signer)
            if tx_status["status"] == "success":
                print("The summoner came back with success from his adventure!")
                self.xp += 250
            elif tx_status["status"] == "pending":
                # Assume success and update xp (so that fast_check_level_up() works)
                self.xp += 250


    ### LEVEL UP ----------------------------

    def xp_required(self):
        return self.level * (self.level + 1) / 2 * 1000

    def fast_check_level_up(self):
        return int(self.xp_required()) <= int(self.xp)

    def check_level_up(self):
        self.update_summoner_info()
        xp_required = self.contracts["summoner"].functions.xp_required(int(self.level)).call() / 1e18
        return int(xp_required) <= int(self.xp)

    def level_up(self):
        # Note the fast check short circuits the long check if False
        if self.fast_check_level_up() and self.check_level_up():
            print(Fore.WHITE + str(self) + " is trying to pass level " + str(self.level + 1) + "!")
            levelup_fun = self.contracts["summoner"].functions.level_up(self.token_id)
            tx_status = self.transacter.sign_and_execute(levelup_fun, gas = 70000, signer = self.signer)
            if tx_status["status"] == "success":
                print(Fore.YELLOW + "Level passed!")
                self.level += 1
                self.xp = 0

    ### CELLAR (CRAFT1) -------------------------------------------

    def time_to_next_cellar(self):
        next_time_available = self.contracts["cellar"].functions.adventurers_log(self.token_id).call()
        current_time = self.transacter.timestamp
        return next_time_available - current_time

    def expected_cellar_loot(self):
        return int(self.contracts["cellar"].functions.scout(self.token_id).call())

    def check_go_cellar(self):
        return self.time_to_next_cellar() <= 0 and self.expected_cellar_loot() > 0

    def go_cellar(self):
        if self.check_go_cellar():
            print(Fore.WHITE + str(self) + " is going to The Cellar")
            cellar_fun = self.contracts["cellar"].functions.adventure(self.token_id)
            tx_status = self.transacter.sign_and_execute(cellar_fun, gas = 120000, signer = self.signer)
            if tx_status["status"] == "success":
                print("The summoner came back from The Cellar with success !")

    def get_balance_craft1(self):
        return self.get_balance_erc20(self.transacter.contracts["craft1"], scaling_factor = 1)

    def transfer_craft1(self, to_id, amount):
        print(Fore.WHITE + "Sending " + str(amount) + " crafting material (I) from " + str(self.token_id) + " to " + str(to_id))
        return self.transfer_erc20(to_id, amount, contract = self.contracts["craft1"], scaling_factor = 1)

    # Generic balance and transfer

    def get_balance_erc20(self, contract, scaling_factor):
        return contract.functions.balanceOf(self.token_id).call() / scaling_factor

    def transfer_erc20(self, to_id, amount, contract, scaling_factor):
        """Transfer tokens:
        to_id: summoner_id of the recipient
        amount: amount to send or "max" to send full balance
        contract: contract (with abi loaded) implementing balanceOf and transfer
        scaling_factor: Factor between UI units and contract units. 1 for craft1, 1e18 for gold."""
        try:
            to_id = int(to_id)
        except ValueError:
            raise InvalidSummonerError("Invalid summoner ID")

        if self.token_id == to_id:
            print(Fore.RED + "Sender is same as recipient: skipping")
            return None

        balance = contract.functions.balanceOf(self.token_id).call()
        # Set amount
        if amount == "max":
            amount = int(balance)
        else:
            try:
                amount = int(int(amount) * scaling_factor)
            except ValueError:
                raise InvalidAmountError("Invalid amount: Must be integer or 'all'.")
        # Check amount
        if amount > balance:
            raise InvalidAmountError("Invalid amount: Sender doesn't have that much.")
        elif amount <= 0:
            print(Fore.RED + "Empty balance: skipping")
            return None 
        # Do the transfer
        transfer_fun = contract.functions.transfer(self.token_id, to_id, amount)
        return self.transacter.sign_and_execute(transfer_fun, gas = 70000, signer = self.signer)

    def transfer_to_new_owner(self, new_owner_address):
        """Transfer the summoner to a new owner"""
        if not new_owner_address.startswith("0x") or len(new_owner_address) != 42:
            raise InvalidAddressError("Invalid address: " + str(new_owner_address))
        if new_owner_address.lower() == self.signer.address.lower():
            raise InvalidAddressError("Invalid address: summoner already belongs to " + str(new_owner_address))
        
        print("Sending " + str(self) + " to " + str(new_owner_address))
        old_address_checksum = Web3.toChecksumAddress(self.signer.address)
        new_address_checksum = Web3.toChecksumAddress(new_owner_address)

        transfer_fun = self.contracts["summoner"].functions.safeTransferFrom(old_address_checksum, new_address_checksum, self.token_id)
        return self.transacter.sign_and_execute(transfer_fun, gas = 70000, signer = self.signer)
