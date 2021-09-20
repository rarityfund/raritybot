from colorama import Fore

class InvalidAmountError(Exception):
    """Used to indicate invalid amounts during transfers"""
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

    def __init__(self, id, transacter):
        # What we need to transact
        self.transacter = transacter
        self.contracts = transacter.contracts
        self.token_id = id
        self.update_summoner_info()
        self.update_gold_balance()

    def __str__(self):
        return "A " + self.class_name + " (" + str(self.token_id) + ")"

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

    def get_balance_gold(self):
        return self.contracts["gold"].functions.balanceOf(self.token_id).call() / 1e18
    
    def update_gold_balance(self):
        self.gold = self.get_balance_gold()

    def check_claim_gold(self):
        claimable_gold = self.contracts["gold"].functions.claimable(self.token_id).call()
        return claimable_gold > 0

    def claim_gold(self):
        if self.check_claim_gold():
            print(Fore.WHITE + str(self) + " is claiming gold")
            claim_gold_fun = self.contracts["gold"].functions.claim(self.token_id)
            tx_status = self.transacter.sign_and_execute(claim_gold_fun, gas = 120000)
            if tx_status["status"] == "success":
                print("The summoner claimed gold with success !")
                self.update_gold_balance()

    def transfer_all_gold(self, to_id):
        self.update_gold_balance()
        return self.transfer_gold(to_id, amount = self.gold)

    def transfer_gold(self, to_id, amount):
        if amount > self.gold:
            raise InvalidAmountError("Summoner doesn't have enough gold")
        if amount <= 0:
            raise InvalidAmountError("Nothing to send")
        transfer_fun = self.contracts["gold"].functions.transfer(self.token_id, to_id, amount)
        return self.transacter.sign_and_execute(transfer_fun, gas = 70000)

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
            tx_status = self.transacter.sign_and_execute(adventure_fun, gas = 70000)
            if tx_status["status"] == "success":
                print("The summoner came back with success from his adventure!")
                self.update_summoner_info()


    ### LEVEL UP ----------------------------

    def xp_required(self):
        return self.level * (self.level + 1) / 2 * 1000

    def fast_check_level_up(self):
        return int(self.xp_required()) <= int(self.xp)

    def check_level_up(self):
        xp_required = self.contracts["summoner"].functions.xp_required(int(self.level)).call() / 1e18
        return int(xp_required) <= int(self.xp)

    def level_up(self):
        # Note the fast check short circuits the long check if False
        if self.fast_check_level_up() and self.check_level_up():
            print(Fore.WHITE + str(self) + " is trying to pass level " + str(self.level) + "!")
            levelup_fun = self.contracts["summoner"].functions.level_up(self.token_id)
            tx_status = self.transacter.sign_and_execute(levelup_fun, gas = 70000)
            if tx_status["status"] == "success":
                print(Fore.YELLOW + "Level passed!")
            else: 
                print(Fore.WHITE + "Transaction failed. The summoner was incapable to pass a new level")


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
            tx_status = self.transacter.sign_and_execute(cellar_fun, gas = 120000)
            if tx_status["status"] == "success":
                print("The summoner came back from The Cellar with success !")

    def get_balance_craft1(self):
        return self.transacter.contracts["craft1"].functions.balanceOf(self.token_id).call()

    def transfer_all_craft1(self, to_id):
        return self.transfer_craft1(to_id, amount = self.get_balance_craft1())

    def transfer_craft1(self, to_id, amount):
        if amount > self.get_balance_craft1():
            raise InvalidAmountError("Summoner doesn't enough crafting material")
        if amount <= 0:
            raise InvalidAmountError("Nothing to send")
        transfer_fun = self.transacter.contracts["craft1"].functions.transfer(self.token_id, to_id, amount)
        return self.transacter.sign_and_execute(transfer_fun, gas = 70000)