# raritybot WIP (devel)

- Now able to assign attributes to newly created summoners, via `--attributes` which takes a JSON-formatted string. For example, `summon --class Fighter --attributes '{"str":20,"dex":10,"const":14,"int":8,"wis":8,"cha":8}'`.

- Printing balance of crafting material (I) in summoner info

- Improved listing of summoner info. Requires NEW DEPENDENCY `tabulate` to install with `pip3 install --user tabulate`. 

# raritybot v1.2.0 (master)

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