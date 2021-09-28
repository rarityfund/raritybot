import json
from raritydata import RarityData
from key import InvalidInputError
from colorama import Fore

class SummoningError(Exception):
    pass

class SummoningEngine:

    def __init__(self, transacter, signer):
        self.transacter = transacter
        self.signer = signer

    def summon_from_class(self, summoner_class):
        """Summon a new summoner of the specified class ID or class name. 
           summoner_class can be either the ID or the class name. Returns the summoner ID"""
        try:
            class_id = int(summoner_class)
        except ValueError:
            try:
                class_id = RarityData.class_names.index(summoner_class)
            except ValueError:
                raise SummoningError("Invalid class name or ID: aborting")
        return self.summon(class_id)

    def summon(self, class_id):
        """Summon a new summoner of the specified class. Returns the summoner ID"""
        try:
            class_name = RarityData.class_from_id(class_id)
        except IndexError:
            raise SummoningError("Invalid class id: aborting")
        summon_fun = self.transacter.contracts["summoner"].functions.summon(class_id)
        tx_status = self.transacter.sign_and_execute(summon_fun, gas = 150000, signer = self.signer)
        if tx_status["status"] == "pending":
            # We will get details from tx receipt later
            return None
        else:
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
            receipt_class_name = RarityData.class_names[receipt_class_id]
            return {"token_id": receipt_token_id, "class_name": receipt_class_name}
        except:
            return None

    def parse_attributes(self, attribute_str):
        try:
            attributes = json.loads(attribute_str)
        except json.decoder.JSONDecodeError as e:
            raise InvalidInputError("Invalid JSON spec for attributes: " + str(e))
        
        # Check keys: should be the 6 attributes
        keys = [k for k in attributes.keys()]
        if keys != RarityData.attribute_names:
            raise InvalidInputError("Attributes don't match. Expecting: " + str(RarityData.attribute_names))

        # Check values: should be integers
        try:
            attributes_int = {k: int(attributes[k]) for k in attributes}
        except ValueError as e:
            raise InvalidInputError("Attributes are not integers: ", str(e))
        
        # Check point buy: should cost 32 points to buy
        ap_needed = self.calculate_point_buy(attributes_int)
        if ap_needed != 32:
            raise InvalidInputError("Attributes should cost 32 AP to buy. Yours cost " + str(ap_needed) + " AP.")

        return attributes_int

    def calculate_point_buy(self, attributes):
        try:
            points_total = self.transacter.contracts["attributes"].functions.calculate_point_buy( 
                attributes["str"], attributes["dex"], attributes["const"], 
                attributes["int"], attributes["wis"], attributes["cha"]).call()
        except:
            points_total = 0
        return points_total


    def set_attributes(self, summoner_id, attributes):
        if self.calculate_point_buy(attributes) != 32:
            raise InvalidInputError("Invalid attribute assignment")

        print(Fore.WHITE + "Summoner " + str(summoner_id) + ": assigning attributes " + str(attributes))
        point_buy_fun = self.transacter.contracts["attributes"].functions.point_buy(summoner_id, 
        attributes["str"], attributes["dex"], attributes["const"], 
        attributes["int"], attributes["wis"], attributes["cha"])

        return self.transacter.sign_and_execute(point_buy_fun, gas = 130000, signer = self.signer)