import json
import copy


def countChildren(node) -> int:
    """Count all children of all nodes in the tree

    Args:
        node (_type_): The node to start with

    Returns:
        int: the number of children of this node
    """
    if "children" in node.keys():
        count = 0
        for child in node["children"]:
            count = count + countChildren(child)
    else:
        count = 1

    node["count"] = count
    return count


def findBestGuess(node) -> str:
    """Find the species down the path of most bisected nodes

    Args:
        node (_type_): The node to start with

    Returns:
        str: A species name to guess
    """
    totalCount = node["count"]
    if "children" in node.keys():
        diffFromHalf = 0.5
        bestChild = None
        for child in node["children"]:
            cDiff = abs(0.5 - (child["count"] / totalCount))
            if cDiff < diffFromHalf:
                diffFromHalf = cDiff
                bestChild = child
            elif cDiff == diffFromHalf:
                if (bestChild is None) or (bestChild["count"] < child["count"]):
                    bestChild = child
        return findBestGuess(bestChild)
    else:
        return node["name"]


def findBestGuessLargest(node) -> str:
    """Find the species down the path of largest counts per-node

    Args:
        node (_type_): The node to start with

    Returns:
        str: A species name to guess
    """
    if "children" in node.keys():
        bestChild = None
        mostKids = 0
        for child in node["children"]:
            if "count" in child.keys():
                thisChildsCount = child["count"]
            else:
                thisChildsCount = 0

            if mostKids < thisChildsCount:
                mostKids = thisChildsCount
                bestChild = child
        return findBestGuessLargest(bestChild)
    else:
        return node["name"]


def getAllSpecies(node):
    speciesList = []
    if "children" in node.keys():
        for child in node["children"]:
            speciesList.extend(getAllSpecies(child))
    else:
        speciesList.append(node["name"])
    return speciesList


def findBestGuessExhaustive(originalNode) -> str:
    # Get a list of all potential guesses
    allSpecies = getAllSpecies(originalNode)

    # Shortcut to always start with mink
    if 255 == len(allSpecies):
        return "mink"

    fewestRemaining = 10000000

    speciesChecked = 0
    for possibleGuess in allSpecies:
        # print(
        #     "{0:0.2f}".format(100 * speciesChecked / len(allSpecies))
        #     + " - checking "
        #     + possibleGuess
        # )
        speciesChecked = speciesChecked + 1
        numRemaining = 0
        for possibleResult in allSpecies:
            tree = copy.deepcopy(originalNode)

            # Find the common group between the guess and the species
            commonGroup = findCommonGroup(tree, possibleGuess, possibleResult)

            # Set the new root to the common group
            tree = newRoot(tree, commonGroup.lower())

            if "children" in tree.keys():
                # Cull the branch under the common group leading to the guess, since that was incorrect
                groupList = findSpecies(tree, possibleGuess)
                for idx in range(len(groupList)):
                    if groupList[idx].lower() == commonGroup.lower():
                        cullGroup(tree, groupList[idx + 1].lower())
                        break

            countChildren(tree)
            numRemaining = numRemaining + tree["count"]

        if (numRemaining / len(allSpecies)) < fewestRemaining:
            fewestRemaining = numRemaining / len(allSpecies)
            bestGuess = possibleGuess

        # print(possibleGuess + " -> " + str(numRemaining / len(allSpecies)))

    # print("BEST GUESS IS " + bestGuess + " WITH " + str(fewestRemaining) + " LEFT")
    return bestGuess


def newRoot(node, group):
    """Find a node in the graph and return it so that it may be set as the new root

    Args:
        node (_type_): The node to start with
        group (_type_): The name of the node to find

    Returns:
        _type_: The found node
    """
    if node["name"].lower() == group:
        return node
    if "children" in node.keys():
        for child in node["children"]:
            if child["name"].lower() == group:
                return child
            else:
                nr = newRoot(child, group)
                if nr is not None:
                    return nr
    return None


def findSpecies(node, species):
    """Find a species in the tree and return a list of all nodes to get from the root to that species

    Args:
        node (_type_): The node to start with
        species (_type_): The name of the species to find

    Returns:
        _type_: An array of node names from the root to the species
    """
    if node["name"] == species:
        return [node["name"]]
    elif "children" in node.keys():
        for child in node["children"]:
            nameList = findSpecies(child, species)
            if nameList is not None:
                nameList.insert(0, node["name"])
                return nameList
    return None


def cullGroup(node, group):
    """Remove a group from the tree

    Args:
        node (_type_): The node to start with
        group (_type_): The name of the group to remove
    """
    # For each child
    if "children" in node.keys():
        for child in node["children"]:
            # If the name matches cull it
            if child["name"].lower() == group:
                node["children"].remove(child)
                return
            else:
                cullGroup(child, group)


def findCommonGroup(tree, guess, species):
    """Find the common group between two species

    Args:
        tree (_type_): The node to start with
        guess (_type_): One species
        species (_type_): The other species

    Returns:
        _type_: The name of the common group for the two species
    """
    guessList = findSpecies(tree, guess)
    speciesList = findSpecies(tree, species)
    for idx in range(min(len(guessList), len(speciesList))):
        if guessList[idx] != speciesList[idx]:
            return guessList[idx - 1]
    return species


def solveForSpecies(tree, species):
    """Automatically solve for a given species

    Args:
        tree (_type_): The node to start with
        species (_type_): Ths species to solve for

    Returns:
        _type_: The number of guesses required to find this species
    """
    bestGuess = ""
    guesses = 1
    while bestGuess != species:
        # Count children again count for next iteration
        countChildren(tree)

        # Find the best guess in the current tree
        bestGuess = findBestGuessLargest(tree)

        # Find the common group between the guess and the species
        commonGroup = findCommonGroup(tree, bestGuess, species)

        # If it's a match
        if bestGuess == species:
            # We're done
            return guesses

        # Set the new root to the common group
        tree = newRoot(tree, commonGroup.lower())

        # Cull the branch under the common group leading to the guess, since that was incorrect
        groupList = findSpecies(tree, bestGuess)
        for idx in range(len(groupList)):
            if groupList[idx].lower() == commonGroup.lower():
                cullGroup(tree, groupList[idx + 1].lower())
                break

        guesses = guesses + 1

    return guesses


################################################################################

# Uncomment this to solve for all species and print data
# with open("metazooa-species.json") as file:
#     mzSpecies = json.load(file)
#     totalSpecies = 0
#     totalGuesses = 0
#     # For each species
#     for species in mzSpecies["species"]:
#         # Reload the tree
#         with open("tree.json") as file:
#             tree = json.load(file)
#             # Solve for the species automatically
#             guesses = solveForSpecies(tree, species)
#             print('"' + species + '", "' + str(guesses) + '"')
#             totalSpecies = totalSpecies + 1
#             totalGuesses = totalGuesses + guesses
#             print("{0:0.2f}".format(100 * totalSpecies / len(mzSpecies["species"])))
#     print("avg: " + str(totalGuesses / totalSpecies))


with open("tree.json") as file:
    tree = json.load(file)

    while True:
        # Count children again count for next iteration
        countChildren(tree)

        # Find the best guess in the current tree
        bestGuess = findBestGuessLargest(tree)

        # Prompt the user
        print("Is it a " + bestGuess + "?")
        commonGroup = input("Common group: ")

        # Set the new root to the common group
        nr = newRoot(tree, commonGroup.lower())
        # If the new root isn't found, it's probably a typo
        if nr is not None:
            # All good
            tree = nr
        else:
            # Prompt the user to try again
            print(commonGroup + " not found. Try again.")
            continue

        # Cull the branch under the common group leading to the guess, since that was incorrect
        groupList = findSpecies(tree, bestGuess)
        for idx in range(len(groupList)):
            if groupList[idx].lower() == commonGroup.lower():
                cullGroup(tree, groupList[idx + 1].lower())
                break
