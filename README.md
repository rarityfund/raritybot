# Rarity bot v1.4.0

_____________________________________________________

**CAREFUL USE THIS SOFTWARE AT YOUR OWN RISKS**

_____________________________________________________


raritybot is a command-line utility to manage your rarity summoners.

## Installation

You need python3 and pip3 installed on your host. 

Before running the code you'll need to install a few dependencies with:

```sh
pip3 install --user web3 colorama argparse tabulate
```

You might also need to install `getpass` on some platforms, with `pip3 install --user getpass`.


Next, clone the repository or simply download the files. Now you can run `rarity.py`!

## Importing a key

Before you can run the bot, you need to import your address and your private key. We recommend using a dedicated account for rarity. It is easy to create extra accounts with e.g. Metamask.

**A PRIVATE KEY IS DIFFERENT FROM A SEED, PLEASE DON'T ENTER YOUR SEED**

On Metamask you can access your private key from the "Account details" panel.

Open a termnial in the directory of `rarity.py` and run:

```sh
# Import a key (to default location privatekeyencrypted.json)
python3 rarity.py import-key

# Or, if you want to specify where to save the key:
python3 rarity.py import-key --keyfile path/to/keyfile.json
```

This will store the private key you paste in an encrypted file `privatekeyencrypted.json` located in the active directory. You'll have to choose a password for that and use this password again every time you want to take actions requiring transactions.

## Running the bot

Once your key is created, you can run the bot simply by opening a terminal in the directory of `rarity.py` and running:

```sh
python3 rarity.py [command] [command arguments] [general arguments]
```

Where `command` is one of the commands listed below, `command arguments` are the command-specific arguments (run `python3 rarity.py [command] --help` to see them) and `general arguments` are common to all commandes.

These general arguments are accepted by all commands:

- `--keyfile [file]`: path to your keyfile if it's not the default `privatekeyencrypted.json`
- `--password [pwd]`: avoid having to interactively enter your password by passing it directly. Useful when setting up cron jobs. You could use `--password "$RARITY_PWD"` to load the password from an environment varuable and avoid having it in plaintext.
- `--txmode {single/batch}`: `single` transaction mode (default) will wait for the tx receipt after each tx whereas `txmode batch` will send many tx at once and wait for all the receipts after. The latter is obviously faster.
- `--maxgasprice [price]`: bot will abort if the gas price is superior to `[price]`, in gwei. The gas price on Fantom Opera is usually between 100 and 600 gwei so `--maxgasprice 200` works well for cron jobs.

These are the available commands:

- `import-key`
- `show` (and its subcommands `show summoners`, `show gas`, `show items`, `show craftable`, `show skills`, etc)
- `run` to run the daily actions like adventure, going to the cellar, etc
- `summon` to create new summoners
- `transfer` to move a certain quantity gold or crafting material around
- `transfer-all` to move ALL the gold or crafting material of a summoner
- `send-summoner` to move a summoner to a new address
- `set-attributes` to set attributes (str, dex, const, int, wis, cha)
- `set-skill` to increase a skill level (e.g. craft)
- `craft` to craft items (or simulate crafting with `--simulate`)
- `setup-crafting` to prepare summoners to craft (set up the relevant contract approvals)

Please refer to `python3 rarity.py --help` for an up-to-date list of all the available commands.

You can see a manual for each command by setting the flag `--help`, for example `python3 rarity.py run --help`.

The bot checks EVERYTHING before taking any actions, so don't worry about running commands as mch as you want. Transactions are only sent if all the conditions are valid.

## Examples

If you want to run those examples yourself, make sure to pass the path to your keyfile with `--keyfile your_key.json`. You can use any general argument like `--maxgasprice [price]` or `--txmode batch` in the commands below.

### Show various things

The `show` command is essential to look up summoner ids, item ids, check the gas, etc. 

```sh
# List summoners on the address
python3 rarity.py show summoners

# Show only the first 3 summoners (faster if you have lots)
python3 rarity.py show summoners -n 3

# List any crafted items on the address
python3 rarity.py show items

# Show gas price and maximum action costs in FTM
python3 rarity.py show gas

# List craftable items (useful to look up item ids, DCs and costs before crafting)
python3 rarity.py show craftable

# Show crafting success probabilities for an item of DC 20
# Note it is more convenient to use a crafting simulation if you already have a crafter in mind
python3 rarity.py show crafting-proba -n 20
```


### Summon new characters

```sh
# Summon a Bard
python3 rarity.py summon Bard

# Summon 2 Barbarians and make them very wise and charismatic -- not recommended :)
python3 rarity.py summon Barbarian -n 2 --attributes '{"str":8, "dex":8, "const":8, "int":11, "wis":18, "cha":17}'
```

### Send you summoners on adventures and dungeons

Your summoner can do lots of actions with the `run` command:

- `list`: show the summoner list
- `adventure`: go on an adventure (if available)
- `cellar`: go to the cellar dungeon to loot crafting material (if available and if the expected loot if at least 5 craft mats)
- `level_up`: level up (when possible)
- `claim_gold`: claim gold (when possible)

By default, the `run` commands does everything. Note you can use the `--maxgasprice [price]` argument to prevent execution when the gas is too expensive.

```sh
# Run the default actions
python3 rarity.py run

# Run adventure only, in batched txmode with is much faster if you have lots of summoners
python3 rarity.py run adventure --txmode batch

# Run adventure and cellar, only if the gas price is under 200 gwei
python3 rarity.py run adventure cellar --maxgasprice 200
```

### Transfering gold and crafting material

Two commands are useful: `transfer` (to send a set amount of gold or craft mats) and `transfer-all` (to send the full balance of the summoner). It is possible to send gold or crafting materials from ALL summoners by specifying `--from all`. This is the default for `transfer-all` if you do not specify `--from`.

See `python3 rarity.py transfer-all --help` for more details.

Note: to prevent silly mistakes, transfers to summoners which do not belong to the loaded address will abort. You will have to pass `--force` to force the transfer to proceed.

```sh
# Send 200 gold from summoner 123 to summoner 456
python3 rarity.py transfer gold --from 123 --to 456 --amount 200

# Send all the gold from summoner 123 to summoner 456
python3 rarity.py transfer-all craft1 --from 123 --to 456 

# Send all crafting material from everyone to summoner 456
python3 rarity.py transfer-all craft1 --to 456

# Note that if the recipient (here 456) does not belong to the loaded address, the transfer will abort unless `--force` is specified.
```

### Transfer summoners to another address

You can transfer one summoner or you can transfer ALL summoners with "all".

Note: transferring all summoners require the `--force` flag, again to prevent costly mistakes.

```sh
# Transfer one summoner to another address
python3 rarity.py send-summoner 123 --to 0x123abc...d89

# Transfer ALL summoners to another address - requires --force
python3 rarity.py send-summoner all --to 0x123abc...d89 --force
```

## Set attributes

You can set attributes when summoning with `summon --attributes`, but you can also set attributes for any existing summoner.

```sh
# Set attributes of one summoner (here 123)
python3 rarity.py set-attributes '{"str":8, "dex":8, "const":8, "int":11, "wis":18, "cha":17}' 123

# Set attributes of multiple summoners
python3 rarity.py set-attributes '{"str":8, "dex":8, "const":8, "int":11, "wis":18, "cha":17}' 123 456 789

# Set attributes of all summoners on the address, with batched tx
python3 rarity.py set-attributes '{"str":8, "dex":8, "const":8, "int":11, "wis":18, "cha":17}' all --txmode batch
```

## Set skills

You can currently only set one skill at a time. Typically, you might want to get the "Craft" skill so you can start crafting objects.

If you know how you want to spend all your skill points, it would be more efficient to assign all skills in one tx, but that's not currently possible.

As with `set-attributes`, you can set skill for one, many or all summoners.

```sh
# See all available skills along with stats, class info, etc
python3 rarity.py show skills

# Set craft skill to lvl 5 for summoner 123
python3 rarity.py set-skill craft 5 123

# Set craft skill to lvl 5 for multiple summoners (here 123, 456 and 789)
python3 rarity.py set-attributes craft 5 123 456 789

# Set craft skill of all summoners on the address, with batched tx
python3 rarity.py set-skill craft 5 all --txmode batch
```

## Preparing to craft

Before a summoner can craft, they must:

1. have attributes (ideally high in INT for a crafter), see `set-attributes`.
2. have the "Craft" skill (the higher the level, the better), see `set-skill`.
3. have approved the crafting contract to spend their XP, their gold and their crafting material.

You can take care of all the approval required with the command `setup-crafting`, for one, many or all summoners. As with most operations, the bot will skip any steps that is not needed for the selected summoners, so you can run the command as much as necessary.

If the flag `--approve-for-all` is set, then the crafting contract will be "approved for all" on your _address_. There are several advantages to using `approve for all` as opposed to the basic `approve`:

- with only 1 tx, the crafting contract will be able to spend the XP from all your summoners
- the crafting approval will be permanent (until explicitly revoked). Otherwise, the basic approval is limited as only one address can be approved at any one time, so approving another contract later will revoke the crafting contract approval.

However, this gives the crafting contract more permissions than strictly needed (like the ability to self-approve to spend tokens). The choice is up to you, but if you have a lot of summoners, you will probably prefer `--approve-for-all`. Note that the bot will still need to approve gold and craft mats spends for each summoner individually.

Examples:
```
# Setup crafting for 3 summoners
python3 rarity.py setup-crafting 2890228 2890220 2890230

# Setup crafting for ALL summoners
python3 rarity.py setup-crafting all

# Setup crafting for ALL summoners with the approve-for-all option
python3 rarity.py setup-crafting all --approve-for-all
```

## Crafting

Once you are prepared to craft (see previous section), you can finally use the `craft` command to craft items. The basic syntax is `craft {good/armor/weapon} [item_id] --crafter [summoner_id] --mats [amount of craft mats]`. You can craft multiple items (or rather, the same item, multiple times) with `-n N` where `N` is an integer, but crafting may stop early if you run out of XP, gold or crafting materials.

To run a crafting simulation, simply run the crafting command with the flag `--simulate`. It will give you the probability of success (given the amount of crafting materials) and tell you how much craft mats you'd have to put to be certain of success. It will also run the `simulate()` function of the crafting contract, so you see how your check ranks against the DC -- but the probability is really the most reliable indicator. 

You can actually run more than one simulation if you want by passing `-n [N]` (running N successive simulations). This can take some time as each simulation is delayed by 4 seconds to ensure it's in a new block (otherwise we'd just get the same result N times). There's really no need to do that though, unless you don't trust our crafting probabilities!

Although you could use any amount of crafting material, the bot only lets you use a multiple of 10 since the DC bonus is based on 10s of craft mats.

```
# Look up the craftable item and pick an item id
python3 rarity.py show craftable

# Simulate the crafting of a great axe (weapon id 35) by summoner 123 with 10 crafting materials
python3 rarity.py craft weapon 35 --crafter 123 --mats 10 --simulate

# Actually craft a great axe (weapon id 35) with summoner 123 using 100 crafting materials
python3 rarity.py craft weapon 35 --crafter 123 --mats 50

# Actually craft of a studded leather armor (armor id 3) with summoner 123 using 50 crafting materials
python3 rarity.py craft armor 3 --crafter 123 --mats 50

# Craft 10 torches using 20 mats each time -- crafting will stop early if you run out of XP, gold or mats
python3 rarity.py craft good 23 --crafter 123 --mats 20

```


*By Olocrom & Asa*

Powered by ftmscan.com and rpc.ftm.tools APIs.

Tips some FTM (on the phantom network) if you liked this 🙂 : 0x128bd256da23c382D3D27a46FEAf32212154f159
