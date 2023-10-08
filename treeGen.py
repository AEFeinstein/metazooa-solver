import re
import json


class taxName:
    def __init__(self, line: str) -> None:
        """Initialize a taxonomic name from a line of names.dmp

        Args:
            line (str): The line from names.dmp
        """
        lineParts = re.split("\s*\|\s*", line)
        self.tax_id = int(lineParts[0])
        self.name_txt = lineParts[1]
        self.unique_name = lineParts[2]
        self.name_class = lineParts[3]


class taxNode:
    def __init__(self, line: str) -> None:
        """Initialize a taxonomic node from a line of nodes.dmp

        Args:
            line (str): The line from nodes.dmp
        """
        lineParts = re.split("\s*\|\s*", line)
        self.tax_id = int(lineParts[0])
        self.parent_tax_id = int(lineParts[1])
        self.rank = lineParts[2]
        self.embl_code = lineParts[3]
        self.division_id = int(lineParts[4])
        self.inherited_div_flag = int(lineParts[5])
        self.genetic_code_id = int(lineParts[6])
        self.inherited_GC_flag = int(lineParts[7])
        self.mitochondrial_genetic_code_id = int(lineParts[8])
        self.inherited_MGC_flag = int(lineParts[9])
        self.GenBank_hidden_flag = int(lineParts[10])
        self.hidden_subtree_root_flag = int(lineParts[11])
        self.comments = lineParts[12]

    def setSciName(self, sciName: str):
        """Add a scientific name for this node

        Args:
            sciName (str): The node's scientific name
        """
        self.sciName: str = sciName


class treeNode:
    def __init__(self, tax_id: int) -> None:
        """Initialize a tree node with an ID and empty set of children

        Args:
            tax_id (int): _description_
        """
        self.tax_id = tax_id
        self.children: list[treeNode] = []
        pass

    def addChild(self, child):
        """Add a child to this node

        Args:
            child (treeNode): The child to add
        """
        if child not in self.children:
            self.children.append(child)

    def addToTree(self, tax_id_chain: list[int]):
        """Add a list of IDs to a tree

        Args:
            tax_id_chain (list[int]): A list of IDs where each next ID is the child of the prior one
        """
        # Make a mutable node
        root: treeNode = self
        # For each index in the ID chain, except the last
        for idx in range(len(tax_id_chain) - 1):
            found = False
            # Check all this node's children
            for child in root.children:
                # If the next ID is a child's ID
                if tax_id_chain[idx + 1] == child.tax_id:
                    # Move to that child and continue
                    found = True
                    root = child
                    break
            # If a child with this ID was not found
            if not found:
                # Create a new child, add it, and continue
                newNode = treeNode(tax_id_chain[idx + 1])
                root.addChild(newNode)
                root = newNode

    def compressTree(self):
        """Compress a tree by removing children that only have one child"""
        # While there is only one child
        while 1 == len(self.children):
            if 0 == len(self.children[0].children):
                # species, steal the ID
                self.tax_id = self.children[0].tax_id
                self.children.clear()
                break
            else:
                # Clade, compress it
                self.children = self.children[0].children

        # Multiple children, compress them
        for child in self.children:
            child.compressTree()

    def addNamesToTree(self, nameDict: dict[int, str], mzNames):
        """Add names to the nodes in the tree

        Args:
            nameDict (dict[int, str]): A dictionary from taxonomic ID to scientific name
            mzNames (_type_): A JSON object of metazooa names
        """
        # If this node has no children, print the common name
        if 0 == len(self.children):
            # Find the common name in mzNames by matching tax_id
            for species in mzNames["species"]:
                if species["tax_id"] == self.tax_id:
                    self.name = species["name"]
                    break
        else:
            # Node has children, write the scientific name
            if self.tax_id == 7776:
                self.name = "Gnathostomata"
            elif self.tax_id == 35060:
                self.name = "Gnathostomata-urchin"
            else:
                self.name = nameDict[self.tax_id]

        # For all children
        for child in self.children:
            # Assign names recursively
            child.addNamesToTree(nameDict, mzNames)

    def printTreeDot(self, file):
        """Print a tree in graphviz form

        Args:
            file (_type_): The file to write to
        """
        # If this node has no children, print the common name
        if 0 == len(self.children):
            # Find the common name in mzNames by matching tax_id
            for species in mzNames["species"]:
                if species["tax_id"] == self.tax_id:
                    # Found the name, write it
                    file.write(
                        str(self.tax_id)
                        + ' [label="'
                        + self.name
                        + '" style=filled fillcolor="gold"]\n'
                    )
                    break
        else:
            # Node has children, write the scientific name
            file.write(str(self.tax_id) + ' [label="' + self.name + '"]\n')

        # For all children
        for child in self.children:
            # Draw the link to the child
            file.write(str(self.tax_id) + " -> " + str(child.tax_id) + "\n")
            # Print recursively
            child.printTreeDot(file)

    def printTreeJson(self, file):
        """Print a tree in json form

        Args:
            file (_type_): The file to write to
        """

        file.write("{\n")
        file.write('"name": "' + self.name + '",\n')
        file.write('"id": "' + str(self.tax_id) + '"')
        if 0 < len(self.children):
            file.write(',\n"children": [')

            first = True
            for child in self.children:
                if first:
                    first = False
                else:
                    file.write(",")
                child.printTreeJson(file)
            file.write("]\n")
        else:
            file.write("\n")

        file.write("}\n")


# Read a list of all scientific names for metazooa species
with open("sciNames.json") as file:
    mzNames = json.load(file)

print("Metazooa scientific names loaded")

# Load a dictionary of all taxonomic names
nameDict: dict[int, str] = {}
linesProc = 0
with open("names.dmp") as file:
    for line in file:
        tn = taxName(line)
        # Only care about scientific names
        if tn.name_class == "scientific name":
            nameDict[tn.tax_id] = tn.name_txt

        # Progress
        linesProc = linesProc + 1
        if 0 == linesProc % 1000000:
            print(str(linesProc) + " lines processed")

print("Taxonomic names loaded")

# Link taxonomic IDs to metazooa species
for mzName in mzNames["species"]:
    mzSciName = mzName["sciName"]
    for key in nameDict.keys():
        if nameDict[key] == mzSciName:
            mzName["tax_id"] = key
            break

print("Taxonomic names linked")

# Load an array of all taxonomic nodes
nodeDict: dict[int, taxNode] = {}
# Get a list of all unique rank values
linesProc = 0
with open("nodes.dmp") as file:
    for line in file:
        # Read the node and set the name from the dict
        tn = taxNode(line)
        tn.setSciName(nameDict[tn.tax_id])
        # add it
        nodeDict[tn.tax_id] = tn

        # Progress
        linesProc = linesProc + 1
        if 0 == linesProc % 1000000:
            print(str(linesProc) + " lines processed")

print("Taxonomic nodes linked")

# Start with the root, all animals start with id 1
root = treeNode(1)

# For each metazooa species
for mzSpecies in mzNames["species"]:
    # Create a chain of tax_ids for this species where each ID is the parent of the next one
    tax_id = mzSpecies["tax_id"]
    tax_id_chain = []
    while True:
        tax_id_chain.insert(0, tax_id)
        if tax_id == 1:
            break
        else:
            tax_id = nodeDict[tax_id].parent_tax_id

    # Add the tax_id chain to the tree
    root.addToTree(tax_id_chain)

print("Taxonomic tree created")

# Compress the tree to remove redundant data
# root.compressTree()

print("Taxonomic tree compressed")

# Add names to the nodes in the tree
root.addNamesToTree(nameDict, mzNames)

print("Taxonomic tree named")

# Print the tree to tree.dot
with open("tree.dot", "w") as file:
    file.write("digraph g {\n")
    root.printTreeDot(file)
    file.write("}\n")

print("DOT file generated")

with open("tree.json", "w") as file:
    root.printTreeJson(file)

print("JSON file generated")
