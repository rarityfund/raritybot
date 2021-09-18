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