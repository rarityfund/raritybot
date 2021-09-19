from summoner import Summoner
from colorama import Fore

class SummoningEngine:

    def __init__(self, transacter):
        self.transacter = transacter

    def summon_from_class(self, summoner_class):
        """Summon a new summoner of the specified class ID or class name. 
           summoner_class can be either the ID or the class name. Returns the summoner ID"""
        try:
            class_id = int(summoner_class)
        except ValueError:
            try:
                class_id = Summoner.classes.index(summoner_class)
            except ValueError:
                print("Invalid class name or ID: aborting")
                return None 
        return self.summon(class_id)

    def summon(self, class_id):
        """Summon a new summoner of the specified class. Returns the summoner ID"""
        try:
            class_name = Summoner.classes[class_id]
        except IndexError:
            print("Invalid class id: aborting")
            return None 
        summon_fun = self.transacter.contracts["summoner"].functions.summon(class_id)
        tx_status = self.transacter.sign_and_execute(summon_fun, gas = 150000)
        details = self.get_details_from_summon_receipt(tx_status["receipt"])
        if details:
            print(Fore.GREEN + "Summoned new " + details["class_name"] + " (ID=" + str(details["token_id"]) + ")")
            return details["token_id"]
        else:
            print("Could not confirm summoner token_id")
            return None

    def get_details_from_summon_receipt(self, receipt):
        try:
            receipt_data = str(receipt.logs[1].data)
            receipt_class_id = int(receipt_data[(1+2):(64+2)], 16)
            receipt_token_id = int(receipt_data[(64+2):], 16)
            receipt_class_name = Summoner.classes[receipt_class_id]
            return {"token_id": receipt_token_id, "class_name": receipt_class_name}
        except:
            return None