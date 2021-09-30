# raritybot 1.4.0

A big release with many new features: setting attributes and skills, approving contracts, crafting simulation (with probabilities), actual crafting, etc.

In all the examples below,  `[...]` could stand for `--keyfile key.json --txmode batch --maxgasprice 200` or any other options.

### Attributes 

Set your attributes with the new command `set-attributes`, taking a JSON-formatted string like `'{"str":20,"dex":10,"const":14,"int":8,"wis":8,"cha":8}'` and a list of summoner ids. It was already possible to set attributes while summoning new characters, but this works on existing summoners. The bot will skip gracefully if attributes are already set or if the provided set is invalid.

Examples:
```
# Set attributes on 3 summoners 2890228 2890220 2890230
python3 rarity.py set-attributes '{"str":20,"dex":10,"const":14,"int":8,"wis":8,"cha":8}' 2890228 2890220 2890230 [...]

# Set attributes on everyone (who doesn't already have attributes)
python3 rarity.py set-attributes '{"str":20,"dex":10,"const":14,"int":8,"wis":8,"cha":8}' all [...]
```

### Skills 

- Set your skills (one at a time) with the new command `set-skill`, taking a skill name and a list of summoner ids.
  The bot will skip gracefully if a summoner cannot increase a skill for any reason.
  
- Use `show skills` to list all available skills along with a thorough description of each.

Examples:
```
# Show available skills
python3 rarity.py show skills

# Set craft to level 5 for 3 summoners 2890228 2890220 2890230
python3 rarity.py set-skill craft 5 2890228 2890220 2890230 [...]

# Set craft to level 5 on for all summoners on the address
python3 rarity.py set-skill craft 5 all [...]
```

### Crafting prerequisite

You need to have your attributes set (preferably with high INT) and the "craft" skill before you can craft anything. 
You then need to approve a number of contract interactions: the crafting contract must be able to spend your XP, your gold and your crafting materials. 

You can see your summoner's crafting status in a new column "Crafter", which will say "yes" is the summoner has all the approvals and the skills required to craft.

You can prepare your summoners for crafting using the new `setup-crafting` command which will set up the relevant approvals. You can prepare a selection of summoners by listing their IDs or all of them with "all". The bot will skip gracefully any steps that is not needed for the selected summoners.

If the flag `--approve-for-all` is set, then the crafting contract will be allowed on your address globally, so all summoners will be able to craft and that approval will be permanent (until revoked). It will only take 1 tx in total rather than 1 per summoner. However, this gives the crafting contract more permissions than strictly needed (like the ability to self-approve to spend tokens). The choice is up to you, but if you have a lot of summoners, you will probably prefer `--approve-for-all`. Note that the bot will still need to approve gold and craft mats spends for each summoner individually.

Examples:
```
python3 rarity.py setup-crafting 2890228 2890220 2890230 [...]
python3 rarity.py setup-crafting all [...]
python3 rarity.py setup-crafting all --approve-for-all [...]
```

### Crafting

Finally, after setting attribute, skills and setting up the approvals, we can also craft with the bot!

- List your crafted items with `show items`.

- List all craftable items, their stats and their DC (i.e. how hard they are to craft) with `show craftable`.
  This is useful to look up the ID of the items you want to craft.

- Craft with `craft [item type] [item id] --crafter [summoner id] --mats [crafting material]`.
  Simulate simply by adding the `--simulate` flag. A crafting simulation will tell you how likely you are to succeed and how much craft mats you need to spend to ensure 100% success rate.

- Using crafting material (craft mats) is optional but greatly improves your chances to craft an item. The more mats you use, the more likely you are to succeed. You can see how crafting probabilities work with `show crafting-probas`.


For example:
```
# See what you can craft
python3 rarity.py show craftable

# Simulating the crafting of a great sword with 100 craft mats
# Don't forget the --simulate flag or you'll actually craft it !!!
python3 rarity.py craft weapon 38 --crafter 2890228 --mats 100 --simulate [...]

# Crafting a studded leather armor - for real
python3 rarity.py craft armor 3 --crafter 2890228 --mats 100 [...]

# Crafting 5 torches - this will craft up to 5 torches but might stop before if you're not able to craft anymore
python3 rarity.py craft good 23 -n 5 --crafter 2890228 --mats 100 [...]

# Display your items
python3 rarity.py show items

```

### Other

- Minor UI improvements

- Misc bug fixes and internal refactoring

- Only requiring address or private key when required. 
  For example, now you can run `show summoners` without password and `show gas` or `show craftable` without even having a keyfile


### Crafting



# raritybot 1.3.3

- Bug fix: calls to `gold_contract.claimable()` must originate from owner or authorised addresses. 
  The default `msg.sender` (0x000...000) passed the check unless an address was authorised on the gold contract, in which case the transaction reverted. 
  Fixed by setting the `from` field to `summoner.owner` when checking gold claims.

- Summoners are now only sent to the cellar if their expected loot is >= 5.

# raritybot 1.3.2

- Start implementing crafting: new command `show crafting-proba -n DC` will show crafting probabilities for an item of a given DC (20 by default) for a range of INT and craft levels. 
  Crafting probabilities only depend on INT level, craft level, item DC and how much crafting mats you're willing to spend.
  Low-probability combinations (<70%) are not shown.

- Add internal methods `Summoner.get_skills()` and `Summoner.get_attributes`. The summoner list now shows the attribute scores.

- New commands `show craftable` to list craftable items (goods, armors and weapons). 
  Also now printing more details of owned items with `show items`

- New argument `-n` or `--limit` to limit the number of summoners or items being printed by `show summoners` (resp. `show items`).
  For example, `python3 rarity.py show summoners -n 10` will fetch data for the first 10 summoners only, which can be much faster.

- Better color management while printing

- New config argument `--maxgasprice P` will abort all operations if the gas price is superior to P in gwei. 
  Gas price fluctuates daily between 130 and 600 gwei as of September 2021 so `--maxgasprice 200` is recommended.

- New command `send-summoner` to transfer summoners to another address. Can send one summoner (`send-summoner 1234 --to 0xa123434...`) or all of them (`send-summoner all --to 0xa1234... --force`). When sending all summoners, `--force` is required for safety.

# raritybot 1.3.1

- Bug fix: any ERC721 token (like a crafted item) was treated like a summoner

- Add command `show items` to list crafted items (from crafting (I) contract). No item info for now, this is very basic.

- Now rate limiting calls to api.ftmscan to 5 requests/s to avoid "Rate limit exceeded" errors. 

# raritybot 1.3.0

- Revamped CLI by using argument groups and subparsers to handle subcommands. 
  Now each command (like `run`, `list`, `summon`, etc) will have its own argument namespace which will make life much easier!
  Each command will also have a dedicated help page! See `python3 rarity.py --help` for the top-level help and
  for example `python3 rarity.py run --help` and ``python3 rarity.py summon --help``.
  
  *IMPORTANT: the command MUST be the first argument. This does NOT work: `python3 rarity.py --keyfile key.json run`*

  This allows each command to take independant positional arguments, which just wasn't possible before.
  This greatly simplifies the interface: 
      * `run` actions can be given directly with `python3 rarity.py run adventure cellar --keyfile key.json`
        The basic `python3 rarity.py run` will still work as intended.
      * `list` (and its new alias `show`) can show summoners, gas and maybe crafting codex soon: 
        See `python3 rarity.py list summoners` or `python3 rarity.py show gas`
        The basic `python3 rarity.py list` will still work as intended.
      * `check_gas` is retired in favor of `list gas` or `show gas`.
      * `summon` summons the class directly: `python3 rarity.py summon Barbarian -n 2`
      * `transfer` and `transfer-all` can handle various assets (gold and craft1 for now):
        `python3 rarity.py transfer gold --from FROM --to TO -n 1000`
        `python3 rarity.py transfer_all craft1 --to TO`
  
  Now that commands are actually independent from each other, the CLI should be more stable even as more commands are added.

- New command `import-key` to replace `--import_key`, which takes an option `--keyfile` argument to specify where to save the file.
  Simply do: `python3 rarity.py import-key --keyfile new_key.json`


- New commands `transfer` and `transfer-all` to manage gold and crafting material. 
  Run `[python3 rarity.py]` `transfer --help` and `transfer-all --help` for details, or see the README for examples.

- Internal refactoring to make `rarity.py` smaller. Parser definition went to `cliparser.py` and command definitions went to `commands.py`

- Improved listing of summoner info. Requires NEW DEPENDENCY `tabulate` to install with `pip3 install --user tabulate`. 

- Printing balance of `craft1` (i.e. `crafting material (I)`) in summoner info

- Now able to assign attributes to newly created summoners, via `--attributes` which takes a JSON-formatted string. For example, `summon --class Fighter --attributes '{"str":20,"dex":10,"const":14,"int":8,"wis":8,"cha":8}'`.

# raritybot v1.2.0

- Add "command" as positional argument. Run the traditional script with `python3 rarity.py run`.
  New commands include "run", "list", "check_gas", "summon" and will include "craft" at some point.

- Only asking for pwd when private key is needed (for example, not for "list" or "check_gas")

- Can now summon summoners with `python3 rarity.py summon --class Bard -n 3`. 
  Class is needed but count is optional (will summon 1 by default). Compatible with `--txmode batch` for the industrial farmers.

- Misc UI improvement:
    * Gas check now includes gas price and cost of summoning
    * Time to next adventure and next cellar (+ cellar loot) now shown in summoner listing

# raritybot v1.1

- Now showing actual tx costs at the end (as opposed to max gas spent)
- New argument `--actions` to control which actions are taken
- New actions `list`, `check_gas`, `adventure`, `cellar`, `level_up`, `claim_gold`
- New argument `--txmode` to enable batch processing (with `--txmode batch`)
- Misc UI inprovements

# raritybot v1.0

- Set up command-line interface, see `--help` or `-h` for details
- New `--keyfile` argument to pass path to keyfile if different from `privatekeyencrypted.json`
- New `--password` argument to pass pwd and skip interactive pwd check. 
  Useful for cron job, however would recommend using an env var 
  and do `--password $RARITY_PWD` to avoid leaving pwd in plaintext in shell history. 
- Misc UI improvement
- Refactoring to make things easier to maintain and extend

# raritybot v0.1

- Script `rarity.py` to send everyone on an adventure, to the cellar, level up, claim gold.