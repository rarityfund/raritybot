from colorama import Fore

class Summoner:
    '''Summoners are characters in rarity'''

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
        """Get a string full of details about the summoner"""
        xp_str = str(round(self.xp)) + "/" + str(round(self.xp_required()))
        return  str(self.token_id) + ": A " + \
                self.class_name.ljust(10, ' ') + \
                "\t level " + str(self.level).rjust(2, ' ') + \
                "\t" + xp_str.rjust(10, ' ') + " xp" + \
                "\t" + str(round(self.gold)).rjust(6, ' ') + " gold" + \
                "\t" + "Next Adv: " + self.seconds_to_hms(self.time_to_next_adventure()) + \
                "\t" + "Next Cellar: " + self.seconds_to_hms(self.time_to_next_cellar()) + \
                " (" + str(self.expected_cellar_loot()) + " loot)"
                

    def seconds_to_hms(self, secs):
        if (secs <= 0):
            return "READY".ljust(9, ' ')
        h = secs // 3600
        secs = secs % 3600
        m = secs // 60
        s = secs % 60
        hms = str(h) + "h" + str(m) + "m" + str(s) + "s"
        return hms.ljust(9, ' ')
    
    def update_summoner_info(self):
        """Update class, level and xp"""
        summoner_info = self.contracts["summoner"].functions.summoner(self.token_id).call()
        self.class_id = summoner_info[2]
        self.class_name = self.class_from_index(summoner_info[2])
        self.level =  summoner_info[3]
        self.xp = summoner_info[0] / 1e18

    def update_gold_balance(self):
        self.gold = self.contracts["gold"].functions.balanceOf(self.token_id).call() / 1e18

    def class_from_index(self, index):
        '''Get class from index (local lookup)'''
        try:
          return self.classes[index]
        except IndexError:
            print("Invalid class ID")
            return "N/A"

    def class_from_index_remote(self, index):
        '''Get class from index (remote lookup)'''
        summoner_class = self.contracts["summoner"].functions.classes(index).call()
        return summoner_class

    def time_to_next_adventure(self):
        """Get time to next adventure in seconds"""
        next_time_available = self.contracts["summoner"].functions.adventurers_log(self.token_id).call()
        current_time = self.transacter.timestamp
        return next_time_available - current_time

    def check_adventure(self):    
        return self.time_to_next_adventure() <= 0

    def force_adventure(self):
        print(Fore.WHITE + str(self) + " has gone on an adventure!")
        adventure_fun = self.contracts["summoner"].functions.adventure(self.token_id)
        tx_status = self.transacter.sign_and_execute(adventure_fun, gas = 70000)
        if tx_status["status"] == "success":
            print("The summoner came back with success from his adventure!")
            self.update_summoner_info()

    def adventure(self):
        if self.check_adventure():
            self.force_adventure()

    def xp_required(self):
        return self.level * (self.level + 1) / 2 * 1000

    def fast_check_level_up(self):
        return int(self.xp_required()) <= int(self.xp)

    def check_level_up(self):
        xp_required = self.contracts["summoner"].functions.xp_required(int(self.level)).call() / 1e18
        return int(xp_required) <= int(self.xp)

    def force_level_up(self):
        print(Fore.WHITE + str(self) + " is trying to pass level " + str(self.level) + "!")
        levelup_fun = self.contracts["summoner"].functions.level_up(self.token_id)
        tx_status = self.transacter.sign_and_execute(levelup_fun, gas = 70000)
        if tx_status["status"] == "success":
            print(Fore.YELLOW + "Level passed!")
        else: 
            print(Fore.WHITE + "Transaction failed. The summoner was incapable to pass a new level")

    def level_up(self):
        # Note the fast check short circuits the long check if False
        if self.fast_check_level_up() and self.check_level_up():
            self.force_level_up()
    
    def check_claim_gold(self):
        claimable_gold = self.contracts["gold"].functions.claimable(self.token_id).call()
        return claimable_gold > 0

    def force_claim_gold(self):
        print(Fore.WHITE + str(self) + " is claiming gold")
        claim_gold_fun = self.contracts["gold"].functions.claim(self.token_id)
        tx_status = self.transacter.sign_and_execute(claim_gold_fun, gas = 120000)
        if tx_status["status"] == "success":
            print("The summoner claimed gold with success !")
            self.update_gold_balance()

    def claim_gold(self):
        if self.check_claim_gold():
            self.force_claim_gold()

    def time_to_next_cellar(self):
        next_time_available = self.contracts["cellar"].functions.adventurers_log(self.token_id).call()
        current_time = self.transacter.timestamp
        return next_time_available - current_time

    def expected_cellar_loot(self):
        return int(self.contracts["cellar"].functions.scout(self.token_id).call())

    def check_go_cellar(self):
        return self.time_to_next_cellar() <= 0 and self.expected_cellar_loot() > 0

    def force_go_cellar(self):
        print(Fore.WHITE + str(self) + " is going to The Cellar")
        cellar_fun = self.contracts["cellar"].functions.adventure(self.token_id)
        tx_status = self.transacter.sign_and_execute(cellar_fun, gas = 120000)
        if tx_status["status"] == "success":
            print("The summoner came back from The Cellar with success !")
    
    def go_cellar(self):
        if self.check_go_cellar():
            self.force_go_cellar()