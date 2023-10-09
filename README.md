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
I tested three strategies for finding that species:
1. Starting at the root of the taxonomic tree, go down the branch which has the most species in it and recurse until you reach a species. This has an average of **4.224** guesses per solution.
1. Iterate through each species as a potential guess. For each guess, iterate through each species as a potential solution. For each combination of potential guess and potential solution, tally how many resulting species there would be. Pick the species with the smallest number of total resulting species. This is very slow. This has an average of **4.231** guesses per solution.
1. Starting at the root of the taxonomic tree, go down the branch which has closest to 50% of the remaining species in it and recurse until you reach a species. This has an average of **4.627** guesses per solution.

Once the tree is constructed, it is searched like so:

1. Find the best guess and give it to the user.
    1. Count how many species each node in the tree has underneath it
    1. Use one of the three aforementioned strategies to find the best guess species
1. Get the common group between the unknown species and the guessed species from the user.
1. Set the root of the tree to the common group (remove all species not in the common group).
1. Remove the branch of the tree from below the root to the guessed species (remove all species that are too similar to the incorrectly guessed species).
1. Return to step 1.
