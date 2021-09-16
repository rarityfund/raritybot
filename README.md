# Rarity bot v0.1

___________________________________________________

**CAREFUL USE THIS SOFTWARE AT YOUR OWN RISKS**

_____________________________________________________


This bot will automatically:

- Level up every summoner in an address who is ready for it
- Claim gold for every summoner ready for it
- Make your summoners go into an adventure
- Farm The Cellar dungeon if there is loot to claim for each summoner

This bot is made to work with one address only.  Delete (or rename) the `privatekeyencrypted.json` file to import a new private key if you want this bot to run on another address. Or you can copy the script to another folder and import another private key.

## Installation

You need python and pip3 installed on your host. 

- on Mac you need typically need to install Xcode.
- on Windows you need to install Visual Studio build tools (C++ build tools) [https://www.youtube.com/watch?v=_keTL9ymGjw](https://www.youtube.com/watch?v=_keTL9ymGjw)
-- on Linux python3 is already installed on most distros.

Before running the code you'll need to install a few dependencies with:

```powershell
pip3 install --user web3 colorama argparse getpass
```

Next, clone the repository or simply download the files. Now you can run `rarity.py`!

## First time run

Before you can run the bot, you need to import a private key to your account. We advise that you select a private key from a dedicated account for rarity you already created on metamask.

**A PRIVATE KEY IS DIFFERENT FROM A SEED, DON'T ENTER YOUR SEED ON THIS PROGRAM**

On Metamask you can access your private key from the "Account details" panel.

Open a shell in the directory of `rarity.py` and run:

```
python3 rarity.py --import-key
```

This will store the private key you paste in an encrypted file `privatekeyencrypted.json` located in the active directory. You'll have to choose a password for that and use this password again every time you run the script.

## Running the script

To run the program, simply open a shell at the location of `rarity.py` and run:

```
python3 rarity.py
```

You're supposed to run this script once a day but the script won't take any actions if there is nothing to do.

## Advanced

The rarity bot can take a number of optional arguments. Run `python3 rarity.py --help` for an up-to-date documentation.

```
usage: rarity.py [-h] [-k KEYFILE] [-p PASSWORD] [--import-key] [--adventure-only]

Manage your rarity summoners

optional arguments:
  -h, --help            show this help message and exit
  -k KEYFILE, --keyfile KEYFILE
                        Path to encrypted keyfile
  -p PASSWORD, --password PASSWORD
                        Password to decrypt the keyfile. Be aware it will be available in plaintext in the shell history. Use of
                        interactive login is preferable if possible.
  --import-key          Import a private key which will be stored encrypted in `privatekeyencrypted.json`)
  --adventure-only      Only call adventure() and nothing else.
```


If your private key is not in the same directory (or if it is not called `privatekeyencrypted.json`), you can provide an alternative keyfile with the `--keyfile KEYFILE`. This allows you to maintain summoners on several addresses.

```
python3 rarity.py --keyfile key1.json
python3 rarity.py --keyfile key2.json
```

To run the bot in a non-interactive setting (e.g. a cron job), you can use `--password "PWD"` to pass the password and skip the interactive login. Note this is not recommended unless you know what you're doing, as the password will then be available in plaintext in the shell history.

The `--adventure-only` flag is useful especially if you have a lot of summoners and want to send them adventuring fast.

## Warning about fees

There is no hard cap for gas price. Currently, the script ask the gas price to the web3 provider, **if fees are very high when you run the script, it will not warn you**.

*By Olocrom & Asa*

Tips some FTM (on the phantom network) if you liked this 🙂 : 0x128bd256da23c382D3D27a46FEAf32212154f159