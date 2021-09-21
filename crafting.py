
from transacter import Transacter

class CraftingEngine:

    def __init__(self, transacter):
        self.transacter = transacter

    def balance_of(self, summoner_id):
        return self.transacter.contracts["craft1"].functions.balanceOf(summoner_id).call()

    def total_supply(self, summoner_id):
        return self.transacter.contracts["craft1"].functions.totalSupply().call()

    def transfer_crafting_material(self, from_id, to_id, amount):
        transfer_fun = self.transacter.contracts["craft1"].functions.transfer(from_id, to_id, amount)
        return self.transacter.sign_and_execute(transfer_fun, gas = 70000)
