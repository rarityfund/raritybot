class RarityData:

    class_names =  ["No class",
        "Barbarian", "Bard", "Cleric",
        "Druid", "Fighter", "Monk",
        "Paladin", "Ranger", "Rogue",
        "Sorcerer", "Wizard"]

    skill_names = ['Appraise', 'Balance', 'Bluff', 'Climb', 
        'Concentration', 'Craft', 'Decipher Script', 'Diplomacy', 
        'Disable Device', 'Disguise', 'Escape Artist', 'Forgery', 
        'Gather Information', 'Handle Animal', 'Heal', 'Hide', 
        'Intimidate', 'Jump', 'Knowledge', 'Listen', 'Move Silently', 
        'Open Lock', 'Perform', 'Profession', 'Ride', 'Search', 
        'Sense Motive', 'Sleight Of Hand', 'Speak Language', 'Spellcraft', 
        'Spot', 'Survival', 'Swim', 'Tumble', 'Use Magic Device', 'Use Rope']

    attribute_names = ["str", "dex", "const", "int", "wis", "cha"]

    @classmethod
    def class_from_id(cls, id):
        return cls.class_names[id]

    @classmethod
    def skill_from_id(cls, id):
        return cls.skill_names[id - 1]
    
    @classmethod
    def attribute_from_id(cls, id):
        return cls.attribute_names[id - 1]