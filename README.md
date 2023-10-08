# Metazooa Solver

Solve [Metazooa](https://metazooa.com/) puzzles, and fast!

# How to use

## Setup

> **Note**
> `metazooa-species.json`, `sciNames.json`, and `tree.json` are provided in this repo, but may not be accurate (generated October 7th, 2023)
>
> If you're happy using those files, skip Setup and go straight to Solving

1. Download taxonomic data from https://ftp.ncbi.nih.gov/pub/taxonomy/. You'll want to get `taxdmp.zip` (or an equivalent), extract `names.dmp` and `nodes.dmp`, and put them in this folder.
1. Make `metazooa-species.json` by grabbing the species from https://metazooa.com/ page source. When the game starts, just search for "octopus." Use the same JSON format.
1. Use `sciScraper.py` to grab the scientific names for each animal in `metazooa-species.json`. This generates `sciNames.json`. It's a slow, Selenium process. Gross. It probably won't work in the near future. That's Selenium!
1. Use `treeGen.py` to generate the taxonomic tree used by the solver. This uses `sciNames.json`, `names.dmp`, and `nodes.dmp` as inputs. It generates `tree.json`.

## Solving

Run the solver, and follow the prompts. 
```bash
python solver.py
```

# Strategy

The goal is to guess a species which will narrow the search space as much as possible for the next iteration.
This is done by finding species which best bisect the remaining species at each taxonomic rank, starting from the root.

Once the tree is constructed, it is searched like so:

1. Find the best guess and give it to the user.
    1. Count how many species each node in the tree has underneath it
    1. Starting from the root node, look at all children of that node and find the one that has closest to 50% of species underneath it. If two children are tied for closest-to-50%, pick the larger one. The best child may have more or less than 50% of species under it.
    1. Recurse, using the best child node as the new root node until a species is found. That species is the best guess.
1. Get the common group between the unknown species and the guessed species from the user.
1. Set the root of the tree to the common group.
1. Remove the branch of the tree from below the root to the guessed species.
1. Return to step 1.
