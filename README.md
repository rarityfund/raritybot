# Rarity bot v1.2.0.9000 (DEVEL version)

___________________________________________________

**CAREFUL USE THIS SOFTWARE AT YOUR OWN RISKS**

_____________________________________________________


This bot will automatically:

- Level up every summoner in an address who is ready for it
- Claim gold for every summoner ready for it
- Make your summoners go into an adventure
- Farm The Cellar dungeon if there is loot to claim for each summoner

## Installation

You need python and pip3 installed on your host. 

- on Mac you need typically need to install Xcode.
- on Windows you need to install Visual Studio build tools (C++ build tools) [https://www.youtube.com/watch?v=_keTL9ymGjw](https://www.youtube.com/watch?v=_keTL9ymGjw)
-- on Linux python3 is already installed on most distros.

Before running the code you'll need to install a few dependencies with:

```sh
pip3 install --user web3 colorama argparse getpass tabulate
```

Next, clone the repository or simply download the files. Now you can run `rarity.py`!

## First time run

Before you can run the bot, you need to import a private key to your account. We advise that you select a private key from a dedicated account for rarity you already created on metamask.

**A PRIVATE KEY IS DIFFERENT FROM A SEED, DON'T ENTER YOUR SEED ON THIS PROGRAM**

On Metamask you can access your private key from the "Account details" panel.

Open a shell in the directory of `rarity.py` and run:

```sh
# Import a key (to default location privatekeyencrypted.json)
python3 rarity.py import-key

# Or, if you want to specify where to save the key:
python3 rarity.py import-key --keyfile path/to/keyfile.json
```

This will store the private key you paste in an encrypted file `privatekeyencrypted.json` located in the active directory. You'll have to choose a password for that and use this password again every time you run the script.

## Running the script

To run the program, simply open a shell at the location of `rarity.py` and run:

```sh
python3 rarity.py run
```

You're supposed to run this script once a day but the script won't take any actions if there is nothing to do.

## Other commands

Beyond "run", the bot can also perform other commands:

- "run" to run actions (by default, adenture, level up, etc). The actions are configurable with `--actions`
- "show" to list the summoners (with `show summoners`), show gas price (with `show gas`), etc
- "summon" to create new summoners of a given class takes optional arguments `-n` (to create more than one) and `--attributes` to set their attributes.
- "transfer" or "transfer-all" to transfer gold or crafting material across summoners.

For more details about those commands, please refer to the manual which you can get with `python3 rarity.py [command] --help`:

```sh
# General help
python3 rarity.py --help

# Help for "run"
python3 rarity.py run --help

# Help for "summon"
python3 rarity.py summon --help

# etc
```

## Examples

Here are a few examples:

```shell
# List summoners (free, no need for pwd)
python3 rarity.py show summoners

# Show gas price and action costs (free, no need for pwd)
python3 rarity.py show gas

# Run full daily routine
python3 rarity.py run
# Run only adventure and cellar
python3 rarity.py run adventure cellar
# Run adventure and cellar in batch mode (faster)
python3 rarity.py run adventure cellar --txmode batch

# Summon a Bard
python3 rarity.py summon Bard
# Summon 2 Fighters
python3 rarity.py summon Fighter -n 2
# Summon 3 Barbarians in batched tx (faster) and set their attributes 
python3 rarity.py summon Barbarian -n 3 --txmode batch --attributes '{"str":16,"dex":12,"const":16,"int":8,"wis":10,"cha":14}'

# Send 200 gold from summoner 123 to summoner 456
python3 rarity.py transfer gold --from 123 --to 456 --amount 200
# Send all the gold from summoner 123 to summoner 456
python3 rarity.py transfer-all craft1 --from 123 --to 456 
# Send all crafting material from everyone to summoner 456
python3 rarity.py transfer-all craft1 --to 456
# Note that if the recipient (here 456) does not belong to the loaded address, the transfer will abort unless `--force` is specified.
```


## Advanced

The rarity bot can run a number of commands with lots of optional arguments. Run `python3 rarity.py --help` and `python3 rarity.py [command] --help` for an up-to-date documentation.

General help:
```
usage: rarity.py [-h] {import-key,show,list,run,summon,transfer,transfer-all} ...

Manage your rarity summoners

optional arguments:
  -h, --help            show this help message and exit

Commands:
  {import-key,show,list,run,summon,transfer,transfer-all}
    import-key          Import a new private key.
    show (list)         Show/list a variety of things, like gas price or summoners.
    run                 Run the bot to take automatic configurable actions.
    summon              Summon new summoners of a given class and optionally set attributes.
    transfer            Transfer ERC20 assets between summoners.
    transfer-all        Transfer all of an ERC20 asset to a particular summoner.

```

Help for `run`:
```
usage: rarity.py run [-h] [-k KEYFILE] [-p PASSWORD] [--txmode {single,batch}] [actions [actions ...]]

positional arguments:
  actions               Actions to take. Will do everything by default. Select one or more from "list" (list Summoners on address), "adventure", "level_up", "claim_gold", "cellar" (send to cellar dungeon)

optional arguments:
  -h, --help            show this help message and exit

configuration:
  -k KEYFILE, --keyfile KEYFILE
                        Path to encrypted keyfile
  -p PASSWORD, --password PASSWORD
                        Password to decrypt the keyfile. Be aware it will be available in plaintext in the shell history. Use of interactive login is preferable if possible.
  --txmode {single,batch}
                        How transactions are processed. "single" to send them one by one and wait for the receipt each time. "batch" to send tx in batches and wait less often.
```


If your private key is not in the same directory (or if it is not called `privatekeyencrypted.json`), you can provide an alternative keyfile with the `--keyfile KEYFILE`. This allows you to maintain summoners on several addresses.

```sh
python3 rarity.py run --keyfile key1.json
python3 rarity.py run --keyfile key2.json
```

To run the bot in a non-interactive setting (e.g. a cron job), you can use `--password "PWD"` to pass the password and skip the interactive login. 
Note this is not recommended unless you know what you're doing, as the password will then be available in plaintext in the shell history. 
One way to avoid that is to use an environment variable and call `python3 rarity.py run --keyfile /path/to/key.json --password "$KEY_PWD"`.

## Using --actions to customise the run

You can control the actions taken by the bot runs on a very granular level using `python3 rarity.py run action1 action2 etc`. 
The available actions are:

- "list": Print the list of summoners
- "adventure": Send summoners on adventure (when possible)
- "level_up": Level up summoners who can
- "claim_gold": Claim gold for summoners who can
- "cellar": Send summoners to the Cellar dungeon (when expected loot > 0)


## Warning about fees

There is no hard cap for gas price. Currently, the script ask the gas price to the web3 provider, **if fees are very high when you run the script, it will not warn you**.

*By Olocrom & Asa*

Tips some FTM (on the phantom network) if you liked this 🙂 : 0x128bd256da23c382D3D27a46FEAf32212154f159