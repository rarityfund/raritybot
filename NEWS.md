# raritybot 1.3.2

- Start implementing crafting: new command `show crafting-proba -n DC` will show crafting probabilities for an item of a give DC (20 by default) for a range of INT and craft level. Crafting probabilities only depend on INT level, craft level, item DC and how much crafting mats you're willing to spend. Low-probability combinations (<70%) are not shown.

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