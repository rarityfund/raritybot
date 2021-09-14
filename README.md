# Rarity bot v0.1

This bot will automatically:

- Level up every summoner in an address who is ready for it
- Claim gold for every summoner ready for it
- Make your summoners go into an adventure
- Farm The Cellar dungeon if there is loot to claim for each summoner

This bot is made to work with one address only.  Delete (or rename) the `privatekeyencrypted.json` file to import a new private key if you want this bot to run on another address. Or you can copy the script to another folder and import another private key.

## How to use

___________________________________________________

**CAREFUL USE THIS SOFTWARE AT YOUR OWN RISKS**

_____________________________________________________

You need python and pip3 installed on your host. 

- on Mac you need to install Xcode.

- on Windows you need to install Visual Studio build tools (C++ build tools) [https://www.youtube.com/watch?v=_keTL9ymGjw](https://www.youtube.com/watch?v=_keTL9ymGjw)

Before running the code you'll need to install the dependencies `web3` and `colorama`.


```powershell
pip3 install --user web3 colorama
```

Now you can run **rarity.py** with:

```
python3 rarity.py
```

If it's the first time you run this script, it'll ask you to import a private key. We advise that you select a private key from a dedicated account for rarity you already created on metamask.


**A PRIVATE KEY IS DIFFERENT FROM A SEED, DON'T ENTER YOUR SEED ON THIS PROGRAM**

On Metamask you can access your private key from the "Account details" panel.

This script will store the private key in an encrypted file located in the running directory (from where you executed rarity.py).
You'll have to choose a password for that and use this password again every time you run the script.

You're supposed to run this script once a day but the script won't take any actions if there is nothing to do.

BE SURE TO EXECUTE THE SCRIPT FROM THE DIRECTORY WHERE THE "privatekeyencrypted.json FILE IS AFTER THE FIRST EXECUTION.

## To do next

- Installing a hard cap for gas price. Currently, the script ask the gas price to the web3 provider, **if fees are very high at the moment you run the script, it will not warn you**.

*By Olocrom*

Tips some FTM (on the phantom network) if you liked this 🙂 : 0x128bd256da23c382D3D27a46FEAf32212154f159