import configparser
import pandas as pd
import time
import os.path
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from fake_useragent import UserAgent
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import keyring
import pickle
import re
import undetected_chromedriver as uc
import random

def main():
    idRegex = r'id="(.*?)"'

    #setup the config parser (where the html identifiers are stored)
    config = configparser.ConfigParser()
    config.read('settings.ini')

    #setup the chrome webdriver
    driver = setupDriver()
    driver.get('https://www.investopedia.com/simulator/')

    #load previously saved cookies
    if (os.path.isfile('cookies.pkl')):
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)

    #login to the website
    login(driver, config)

    #click the trade button on website and halt
    waitToLoad(driver, By.XPATH, config.get('tradePath', 'tradeB'))
    driver.find_element(By.XPATH, config.get('tradePath', 'tradeB')).click()
    haltStep()

    #read the excel file as a dataframe
    df = pd.read_excel(r'orders.xlsx', sheet_name='Sheet1')

    #for ever row in the orders.xlsx file we will fill it out on the website
    for index, row in df.iterrows():
        #enter stock ticker into search bar
        waitToLoad(driver, By.CLASS_NAME, config.get('tradePath', 'dropDown'))
        dropdownSelect = driver.find_elements(By.CLASS_NAME, config.get('tradePath', 'dropDown'))

        #enter the selected stock from the file into the search box and halt
        stockInput = getIDs(driver, config, idRegex, False, element=dropdownSelect[0])
        waitToLoad(driver, By.ID, stockInput[0])
        driver.find_element(By.ID, stockInput[0]).send_keys(row.get('Stock'))
        haltStep()

        #click the corresponding stock in the drop-down menu and halt
        tickerIDs = getIDs(driver, config, idRegex, True, pathHeading='tradePath', pathItem='dropDownList')
        enterDropDownVal(driver, tickerIDs, row.get('Stock'))
        haltStep()

        #click the action dropdown and fill it out and then halt
        searchAndClickDropDown(driver, config, idRegex, 'tradePath', dropdownSelect[1], 'dropDownList', row.get('Action'))
        haltStep()

        #fill in the quantity and halt
        quantityInput = getIDs(driver, config, idRegex, True, pathHeading='tradePath', pathItem='quantity')
        waitToLoad(driver, By.ID, quantityInput[0])
        driver.find_element(By.ID, quantityInput[0]).send_keys(row.get('Quantity'))
        haltStep()

        #fill in the order type and halt
        searchAndClickDropDown(driver, config, idRegex, 'tradePath', dropdownSelect[2], 'dropDownList', row.get('Order Type'))
        haltStep()

        #fill in the duration and halt
        searchAndClickDropDown(driver, config, idRegex, 'tradePath', dropdownSelect[3], 'dropDownList', row.get('Duration'))
        haltStep()

        #click the preview order button and halt
        waitToLoad(driver, By.CLASS_NAME, config.get('tradePath', 'previewOrderB'))
        driver.find_element(By.CLASS_NAME, config.get('tradePath', 'previewOrderB')).click()
        haltStep()

        #click the confirm order button (it uses the same css class as the preview button) and halt
        waitToLoad(driver, By.CLASS_NAME, config.get('tradePath', 'previewOrderB')[1])
        driver.find_elements(By.CLASS_NAME, config.get('tradePath', 'previewOrderB'))[1].click()
        haltStep()

        #click the button to go back to the order screen and halt
        waitToLoad(driver, By.LINK_TEXT, "click here")
        driver.find_element(By.LINK_TEXT, "click here").click()
        haltStep()
    
    #dump the cookies back into the file
    pickle.dump(driver.get_cookies(), open('cookies.pkl', 'wb'))

    #driver quits
    driver.quit()

#setup the driver
def setupDriver():
    options = Options()
    options.add_argument(f'user-agent={UserAgent().random}')
    options.add_argument("--start-maximized")
    #fill in this line if you want to use your own user data
    #options.add_argument("user-data-dir=")
    driver = uc.Chrome(options=options, executable_path='chromedriver.exe')
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.implicitly_wait(10)
    return driver

#logins the user to the website
def login(driver, config):
    driver.find_element(By.XPATH, config.get('loginPath', 'loginLink')).click()
    haltStep()   
    driver.find_element(By.XPATH, config.get('loginPath', 'userName')).send_keys(keyring.get_password("investopedia", 'userLogin'))
    haltStep()  
    driver.find_element(By.XPATH, config.get('loginPath', 'password')).send_keys(keyring.get_password('investopedia', 'userName'))
    haltStep()
    driver.find_element(By.XPATH, config.get('loginPath', 'loginB')).click()
    haltStep()

#gets IDs from the innerHTML of a parent HTML section
def getIDs(driver, config, regexInput, searchClass, pathHeading=None, pathItem=None, element=None):
    innerHTML = ''
    if searchClass == True:
        #find the HTML code for the dynamic listbox (for selecting from the listbox)
        waitToLoad(driver, By.CLASS_NAME, config.get(pathHeading, pathItem))
        elements = driver.find_elements(By.CLASS_NAME, config.get(pathHeading, pathItem))
        innerHTML = elements[len(elements)-1].get_attribute('innerHTML')
    else:
        innerHTML = element.get_attribute('innerHTML')

    #find the id of the first element in the listbox and grab it
    ids = re.findall(regexInput, innerHTML)
    return ids
    
#helper method for searchAndClickDropDown, will search all items in a drop down list
def enterDropDownVal(driver, ids, rowValue):
    for actionID in ids:
        #check to see if the stock from the file is listed in the list results
        waitToLoad(driver, By.ID, actionID)
        actionText = driver.find_element(By.ID, actionID).get_attribute('innerHTML')
        actionValue = re.search(rowValue, actionText)

        if (actionValue != None):
            #confirm the stock is the same as the one in the file
            if (actionValue.group() == rowValue):
                waitToLoad(driver, By.ID, actionID)
                driver.find_element(By.ID, actionID).click()
                break

#clicks the dropdown to open and submits the option from the excel file
def searchAndClickDropDown(driver, config, idRegex, pathHeading, dropDownPath, dropDownList, rowVal):
    dropDownPath.click()
    ids = getIDs(driver, config, idRegex, True, pathHeading=pathHeading, pathItem=dropDownList)
    enterDropDownVal(driver, ids, rowVal)

#makes sure an element loads before clicking it
def waitToLoad(driver, byType, identifier):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((byType, identifier)))
    except:
        TimeoutException

#randomly stops the script between 1-3 seconds (to avoid detection)
def haltStep():
    int = random.randint(1, 3)
    time.sleep(int)

if __name__ == "__main__":
    main()