# How to use

1. Download taxonomic data from https://ftp.ncbi.nih.gov/pub/taxonomy/. You'll want to get `taxdmp.zip` (or an equivalent), extract `names.dmp` and `nodes.dmp`, and put them in this folder.
1. Make `metazooa-species.json` by grabbing the species from https://metazooa.com/ page source. When the game starts, just search for "octopus."
1. Use `sciScraper.py` to grab the scientific names for each animal in `metazooa-species.json`. This generates `sciNames.json`. It's a slow, Selenium process. Gross. It probably won't work in the near future. That's Selenium!
1. Use `treeGen.py` to generate the taxonomic tree used by the game. This uses `sciNames.json`, `names.dmp`, and `nodes.dmp` as inputs. It generates `tree.json`
    > **Note**
    > `metazooa-species.json`, `sciNames.json`, and `tree.json` are provided in this repo, but may not be accurate (generated October 7th, 2023)
1. Use `solver.py` to solve the puzzle. It uses `tree.json`. Follow the prompts.
