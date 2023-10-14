from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json
import time
import sys


def recursiveCheckChildren(children: list, commonName: str) -> str:
    for child in children:
        if "children" in child.keys():
            foundName = recursiveCheckChildren(child["children"], commonName)
            if foundName is not None:
                return foundName
        elif "scientificName" in child.keys():
            if commonName == child["name"].casefold():
                return child["scientificName"]
    return None


def findScientificName(guessName: str, checkMetazooa: bool) -> str:
    # driver = webdriver.Firefox()
    # driver.get("https://metazooa.com/game?EnterGame=")
    # # guessInput: WebElement = driver.find_element('name', 'guess')
    # guessInput: WebElement = driver.find_element(By.ID, 'headlessui-combobox-input-P0-0')
    # guessInput.send_keys(guessName)
    # guessInput.send_keys(Keys.RETURN)

    driver = webdriver.Firefox()
    if checkMetazooa:
        driver.get("https://metazooa.com/")
    else:
        driver.get("https://flora.metazooa.com/")

    try:
        enterButton: WebElement = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "EnterGame"))
        )
        enterButton.click()
        guessInput = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "headlessui-combobox-input-P0-0"))
        )  # This is a dummy element
        guessInput.send_keys(guessName)
        guessInput.send_keys(Keys.RETURN)
        time.sleep(5)
        gameJson: WebElement = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "__FRSH_STATE"))
        )  # This is a dummy element
        jsonStr = gameJson.get_attribute("innerHTML")
        mzJson = json.loads(jsonStr)
        mzTree = mzJson["v"][0][1]["data"]["children"]
        return recursiveCheckChildren(mzTree, guessName.casefold())
    finally:
        driver.quit()


# Read a list of all species metazooa cares about

species_filename = "species.json"
sciNames_filename = "sciNames.json"
checkMetazooa = True
if 1 < len(sys.argv):
    if "metaflora" == sys.argv[1].lower():
        species_filename = "species-flora.json"
        sciNames_filename = "sciNames-flora.json"
        checkMetazooa = False

with open(species_filename) as file:
    mzSpecies = json.load(file)

with open(sciNames_filename, "w") as file:
    file.write('{"species":[')
    first = True
    for species in mzSpecies["species"]:
        found = False
        while not found:
            try:
                sciName = findScientificName(species, checkMetazooa)
                if first:
                    first = False
                    file.write("\n")
                else:
                    file.write(",\n")
                file.write('{"name":"' + species + '", "sciName":"' + sciName + '"}')
                file.flush()
                found = True
            except:
                pass

    file.write("]}\n")
