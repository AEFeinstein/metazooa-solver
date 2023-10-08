import json


def countChildren(node):
    if "children" in node.keys():
        count = 0
        for child in node["children"]:
            count = count + countChildren(child)
    else:
        count = 1

    node["count"] = count
    return count


def findBestGuess(node):
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


def newRoot(node, group):
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
    # For each child
    if "children" in node.keys():
        for child in node["children"]:
            # If the name matches cull it
            if child["name"].lower() == group:
                node["children"].remove(child)
                return
            else:
                cullGroup(child, group)


with open("tree.json") as file:
    tree = json.load(file)

countChildren(tree)

while True:
    # Find the best guess in the current tree
    bestGuess = findBestGuess(tree)

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

    # Count children again count for next iteration
    countChildren(tree)
