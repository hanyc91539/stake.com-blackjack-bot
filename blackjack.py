from datetime import datetime
from time import sleep
from threading import Thread
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
import keyboard
import random
import requests

RESULT_WINN = "Win"
RESULT_LOSS = "Loss"

initialBetAmount = 0.0001

HAND_HARD = "Hard"
HAND_SOFT = "Soft"
HAND_PAIR = "Pairs"
HAND_INSURANCE = "Insurance"

BUTTON_BET = 'Bet'
BUTTON_HALF = '1/2'
BUTTON_MULTIPLE = '2x'
BUTTON_HIT = 'Hit'
BUTTON_STAND = 'Stand'
BUTTON_SPLIT = 'Split'
BUTTON_DOUBLE = 'Double'
BUTTON_ACCEPT_INSURANCE = 'Accept insurance'
BUTTON_NO_INSURANCE = 'No insurance'

ID = {
    BUTTON_BET: "bet-button",
    BUTTON_HALF: "input-button-wrap@0",
    BUTTON_MULTIPLE: "input-button-wrap@1",
    BUTTON_HIT : "actions@0",
    BUTTON_STAND : "actions@1",
    BUTTON_SPLIT : "actions@2",
    BUTTON_DOUBLE : "actions@3",
    BUTTON_ACCEPT_INSURANCE : "actions@0",
    BUTTON_NO_INSURANCE : "actions@1",
}

pressedKey = False

Is_End = False

url = "https://stake.com/casino/games/blackjack"

options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9035") #9035
options.add_argument("user-agent=Chrome/121.0.6167.185")
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)


def clickButton(buttonName):
    result = False
    if not pressedKey and buttonName:
        button = None
        buttonId = ID[buttonName]
        if "@" in buttonId:
            button = findElement(driver, By.CLASS_NAME, buttonId.split("@")[0]).find_elements(By.TAG_NAME, 'button')[int(buttonId.split("@")[1])]
        else:
            button = findElement(driver, By.CSS_SELECTOR,f'button[data-testid="{ID[buttonName]}"]')
        if button != None and button.text == buttonName:
            if button.get_attribute("data-test-action-enabled") == "true":
                try:
                    button.click()
                    print(f'{datetime.now().strftime("%H:%M:%S")}, button clicked <{buttonName}>')
                except:
                    driver.execute_script("arguments[0].click();", button)
                sleep(0.5)
                result = True
            else:
                # print(f'{datetime.now().strftime("%H:%M:%S")}, button disabled <{buttonName}>')
                pass
    return result


def findElement(driver, by, value):
    element = None
    while not pressedKey:
        try:
            element = driver.find_element(by, value)
            break
        except:
            pass
        sleep(0.1)
    return element


def getBankRoll():
    bankrollElement = findElement(driver, By.CLASS_NAME, 'coin-toggle')
    if bankrollElement != None:
        bankroll = float(bankrollElement.text)
        return bankroll


def setBetAmount(betAmount):
    while True:
        betAmountInput = findElement(driver, By.CLASS_NAME, 'input-content').find_element(By.TAG_NAME, 'input')
        try:
            betAmountInput.send_keys(str(betAmount))
            print(f'{datetime.now().strftime("%H:%M:%S")}, Bet Amount: {betAmount}')
            break
        except:
            pass
        sleep(0.1)
    sleep(0.5)


def pressKey():
    global pressedKey
    while not Is_End:
        if keyboard.is_pressed('esc'):
            pressedKey = True
            print(
                f'{datetime.now().strftime("%H:%M:%S")}, Pressed the [ESC] key\n')
        sleep(0.1)


def getTheResult(countOfCards, actionType, index, splitted):
    result = {
        "typeOfHand" : "",
        "valueOfDealer" : 0,
        "valueOfPlayer" : 0,
        "countOfNewCards" : 0,
        "countOfPlayerCards" : 0,
        "Is_insurance" : False
    }
    
    if index == 2:
        sleep(7.0)
    
    index = min(index, 1)
    
    while not pressedKey:
        try:
            text = findElement(driver, By.CSS_SELECTOR,f'button[data-testid="{ID[BUTTON_BET]}"]').text
            if text == "Bet":
                break
        except:
            pass
        sleep(0.1)
    if (not splitted and index == 0) and (actionType == BUTTON_STAND or actionType == BUTTON_DOUBLE):
        while True:
            try:
                if findElement(driver, By.CSS_SELECTOR,f'button[data-testid="{ID[BUTTON_BET]}"]').get_attribute("data-test-action-enabled") == "true":
                    break
            except:
                pass
            sleep(0.1)
    if actionType == BUTTON_HIT:
        sleep(2.0)
    
    while not pressedKey:
        try:
            hands = findElement(driver, By.CLASS_NAME, 'hands')
            dealer= hands.find_element(By.CLASS_NAME, 'dealer').text.split('\n')
            playerElement = hands.find_element(By.CLASS_NAME, 'player')
            player = playerElement.find_elements(By.CLASS_NAME, "hand-wrap")[index].text.split('\n')
            countOfNewCards = len(dealer) + len(playerElement.text.split('\n'))
            
            value = dealer[-1]
            insurance = value == '1, 11'

            if ', ' in value:
                value = value.split(', ')[1]
            dealerValue = int(value)

            value = player[-1]
            if ', ' in value:
                value = value.split(', ')[1]
            playerValue = int(value)

            playerCards = player[:-1]
            countOfPlayerCards = len(playerCards)
            
            if dealerValue >= 21 or index == 1 or (countOfNewCards != countOfCards and ((countOfCards == 0 and len(dealer) <= 3 and len(player) == 3) or (countOfCards > 0 and len(dealer) >= 2 and len(player) >= 3))):
                handType = HAND_HARD
                if len(playerCards) == 2:
                    if playerCards[0] == playerCards[1]:
                        if not splitted:
                            handType = HAND_PAIR
                        else:
                            handType = HAND_HARD
                    elif "A" in "".join(playerCards) and playerValue >= 13:
                        handType = HAND_SOFT
                    else:
                        pass
                else:
                    pass
                result["typeOfHand"] = handType
                result["valueOfDealer"] = dealerValue
                result["valueOfPlayer"] = playerValue
                result["countOfNewCards"] = countOfNewCards
                result["countOfPlayerCards"] = countOfPlayerCards
                result["Is_insurance"] = insurance
                break
        except:
            pass
        sleep(0.1)
    sleep(1.0)
    return result


def Strategy():
    global Is_End
    global pressedKey

    betAmount = initialBetAmount
    countWinn, countLoss = 0, 0
    dealerOldValue = 0
    countOfOldCards, actionType, index, splitted = 0, None, 0, False
    splitValues = []

    setBetAmount(betAmount)
    clickButton(BUTTON_BET)
    prevBankroll = getBankRoll()
    
    while not Is_End:
        result = getTheResult(countOfOldCards, actionType, index, splitted)
        handNewType = result["typeOfHand"]
        dealerNewValue = result["valueOfDealer"]
        playerNewValue = result["valueOfPlayer"]
        countOfNewCards = result["countOfNewCards"]
        countOfPlayerCards = result["countOfPlayerCards"]
        insurance = result["Is_insurance"]
        
        if not pressedKey:
            if insurance:
                clickButton(BUTTON_NO_INSURANCE)
                while True:
                    try:
                        actionElements = findElement(driver, By.CLASS_NAME, 'actions').find_elements(By.TAG_NAME, 'button')
                        if len(actionElements) == 4:
                            break
                    except:
                        pass
                    sleep(0.1)

            currBankroll = getBankRoll()

            if not splitted and ((dealerOldValue != 0 and dealerOldValue != dealerNewValue) or dealerNewValue >= 21 or playerNewValue >= 21):
                result = "Push"
                if (playerNewValue == 21 and dealerNewValue < 21) or (playerNewValue <= 21 and dealerNewValue > 21):
                    countWinn += 1
                    result = "Winn"
                elif (playerNewValue < 21 and dealerNewValue == 21) or (playerNewValue > 21 and dealerNewValue <= 21):
                    countLoss += 1
                    result = "Loss"
                elif (playerNewValue > 21 and dealerNewValue > 21) or (playerNewValue == 21 and dealerNewValue == 21):
                    pass
                else:
                    if playerNewValue > dealerNewValue:
                        countWinn += 1
                        result = "Winn"
                    elif playerNewValue == dealerNewValue:
                        pass
                    else:
                        countLoss += 1
                        result = "Loss"
                
                print(f'{datetime.now().strftime("%H:%M:%S")}, {result}({playerNewValue} : {dealerNewValue}), Current {currBankroll} -> Goal {prevBankroll}\n')

                if countWinn + countLoss == 5:
                    if countWinn > countLoss:
                        if prevBankroll <= currBankroll:
                            prevBankroll = currBankroll
                            betAmount = initialBetAmount
                    else:
                        betAmount *= 2
                    countWinn, countLoss = 0, 0
                
                if prevBankroll <= currBankroll:
                    prevBankroll = currBankroll
                    betAmount = initialBetAmount
                    countWinn, countLoss = 0, 0
                
                setBetAmount(betAmount)
                clickButton(BUTTON_BET)
                dealerOldValue = 0
                countOfOldCards = 0
                actionType = None
                continue
            
            if splitted and index == 2 and (actionType == BUTTON_STAND or playerNewValue >= 21 or actionType == BUTTON_DOUBLE):
                for value in splitValues:
                    result = "Push"
                    if (value == 21 and dealerNewValue < 21) or (value <= 21 and dealerNewValue > 21):
                        countWinn += 1
                        result = "Winn"
                    elif (value < 21 and dealerNewValue == 21) or value > 21:
                        countLoss += 1
                        result = "Loss"
                    elif value == 21 and dealerNewValue == 21:
                        pass
                    else:
                        if value > dealerNewValue:
                            countWinn += 1
                            result = "Winn"
                        elif value == dealerNewValue:
                            pass
                        else:
                            countLoss += 1
                            result = "Loss"
                    print(f'{datetime.now().strftime("%H:%M:%S")}, {result}({value} : {dealerNewValue}), Current {currBankroll} -> Goal {prevBankroll}')
                
                if countWinn + countLoss == 5:
                    if countWinn > countLoss:
                        if prevBankroll <= currBankroll:
                            prevBankroll = currBankroll
                            betAmount = initialBetAmount
                    else:
                        betAmount *= 2
                    countWinn, countLoss = 0, 0

                if prevBankroll <= currBankroll:
                    prevBankroll = currBankroll
                    betAmount = initialBetAmount
                    countWinn, countLoss = 0, 0
                
                print("")

                setBetAmount(betAmount)
                clickButton(BUTTON_BET)
                splitValues = []
                dealerOldValue = 0
                countOfOldCards = 0
                index = 0
                splitted = False
                actionType = None
                continue

            hit, stand, split, double = False, False, False, False
            
            if handNewType == HAND_HARD:
                if countOfPlayerCards == 2:
                    double = double or playerNewValue == 9  and 3 <= dealerNewValue and dealerNewValue <= 6
                    double = double or playerNewValue == 10 and 2 <= dealerNewValue and dealerNewValue <= 9
                    double = double or playerNewValue == 11 and 2 <= dealerNewValue and dealerNewValue <= 10
                    hit = hit or playerNewValue == 11 and (dealerNewValue < 2 or dealerNewValue > 10)
                    stand = stand or playerNewValue == 12 and 4 <= dealerNewValue and dealerNewValue <= 6
                    stand = stand or playerNewValue >= 13 and playerNewValue <= 16 and 2 <= dealerNewValue and dealerNewValue <= 6
                    hit = hit or playerNewValue <= 8
                    hit = hit or playerNewValue == 9  and (dealerNewValue < 3 or dealerNewValue > 6)
                    hit = hit or playerNewValue == 10 and (dealerNewValue < 2 or dealerNewValue > 9)
                    hit = hit or playerNewValue == 12 and (dealerNewValue < 4 or dealerNewValue > 6)
                    hit = hit or playerNewValue >= 13 and playerNewValue <= 16 and (dealerNewValue < 2 or dealerNewValue > 6)
                else:
                    hit = hit or playerNewValue >= 5 and playerNewValue <= 11
                    hit = hit or playerNewValue >= 12 and playerNewValue <= 16 and dealerNewValue >= 7
                    stand = stand or playerNewValue >= 12 and playerNewValue <= 16 and dealerNewValue < 7
                stand = stand or playerNewValue >= 17 and playerNewValue < 21
                
            if handNewType == HAND_SOFT:
                if countOfPlayerCards == 2:
                    double = double or (playerNewValue == 13 or playerNewValue == 14) and 5 <= dealerNewValue and dealerNewValue <= 6
                    double = double or (playerNewValue == 15 or playerNewValue == 16) and 4 <= dealerNewValue and dealerNewValue <= 6
                    double = double or playerNewValue == 17 and 3 <= dealerNewValue and dealerNewValue <= 6
                    double = double or playerNewValue == 18 and 3 <= dealerNewValue and dealerNewValue <= 6
                    stand = stand or playerNewValue == 18 and (dealerNewValue == 2 or dealerNewValue == 7 or dealerNewValue == 8)
                    hit = hit or (playerNewValue == 13 or playerNewValue == 14) and (dealerNewValue < 5 or dealerNewValue > 6)
                    hit = hit or (playerNewValue == 15 or playerNewValue == 16) and (dealerNewValue < 4 or dealerNewValue > 6)
                    hit = hit or playerNewValue == 17 and (dealerNewValue < 3 or dealerNewValue > 6)
                    hit = hit or playerNewValue == 18 and (dealerNewValue < 2 or dealerNewValue > 8)
                else:
                    hit = hit or (playerNewValue >= 13 and playerNewValue <= 17)
                    hit = hit or playerNewValue == 18 and dealerNewValue >= 9
                    stand = stand or playerNewValue == 18 and dealerNewValue >= 2 and dealerNewValue <= 8
                stand = stand or 19 <= playerNewValue and playerNewValue < 21
            
            if handNewType == HAND_PAIR:
                split = playerNewValue == 2 or playerNewValue == 22 or playerNewValue == 16
                split = split or (playerNewValue == 4 or playerNewValue == 6) and 2 <= dealerNewValue and dealerNewValue <= 7
                split = split or playerNewValue == 12 and 2 <= dealerNewValue and dealerNewValue <= 6
                split = split or playerNewValue == 14 and 2 <= dealerNewValue and dealerNewValue <= 7
                split = split or playerNewValue == 18 and ((2 <= dealerNewValue and dealerNewValue <= 6) or dealerNewValue == 8 or dealerNewValue == 9)
                double = playerNewValue == 10 and 2 <= dealerNewValue and dealerNewValue <= 9
                stand = stand or playerNewValue == 18 and (dealerNewValue == 7 or dealerNewValue == 10 or dealerNewValue == 11)
                stand = stand or playerNewValue == 20
                hit = hit or playerNewValue == 8
                hit = hit or (playerNewValue == 4 or playerNewValue == 6) and (dealerNewValue < 2 or dealerNewValue > 7)
                hit = hit or playerNewValue == 10 and (dealerNewValue < 2 or dealerNewValue > 9)
                hit = hit or playerNewValue == 12 and (dealerNewValue < 2 or dealerNewValue > 6)
                hit = hit or playerNewValue == 14 and (dealerNewValue < 2 or dealerNewValue > 7)

            if hit:
                actionType = BUTTON_HIT
            elif stand:
                actionType = BUTTON_STAND
            elif split:
                actionType = BUTTON_SPLIT
                splitted = True
            elif double:
                actionType = BUTTON_DOUBLE
            else:
                actionType = None

            result = clickButton(actionType)
            if not (result or splitted):
                if actionType == BUTTON_DOUBLE:
                    actionType = BUTTON_HIT
                    clickButton(actionType)
                else:
                    actionType = None
            sleep(1.0)

            if splitted:
                if actionType == BUTTON_STAND or playerNewValue >= 21:
                    splitValues.append(playerNewValue)
                    index += 1
                if actionType == BUTTON_DOUBLE:
                    result= getTheResult(countOfOldCards, actionType, index, splitted)
                    handNewType = result["typeOfHand"]
                    dealerNewValue = result["valueOfDealer"]
                    playerNewValue = result["valueOfPlayer"]
                    countOfNewCards = result["countOfNewCards"]
                    countOfPlayerCards = result["countOfPlayerCards"]
                    insurance = result["Is_insurance"]
                    
                    splitValues.append(playerNewValue)
                    index += 1
            
            dealerOldValue, countOfOldCards = dealerNewValue, countOfNewCards
        else:
            print("\n")
            response = input("It has now stopped running. Press the [y] key to run again, the [n] key to exit.")
            if response == "y":
                print("\n")
                input("To run it again, you need to reset all states. Press the [Enter] key after initializing.")
                print("\n")
                pressedKey = False
                betAmount = initialBetAmount
                countWinn, countLoss = 0, 0
                dealerOldValue = 0
                countOfOldCards, actionType, index, splitted = 0, None, 0, False
                splitValues = []
                
                setBetAmount(betAmount)
                clickButton(BUTTON_BET)
                prevBankroll = getBankRoll()                
            else:
                break
    print(f'{datetime.now().strftime("%H:%M:%S")}, Ended')
    Is_End = True


def userVerify(url, payload):    
    global pressedKey
    global Is_End
    
    while True:
        sleep(3600)
        response = requests.request("POST", url, data=payload)
        data = response.json()["data"]
        print("")
        print(data + "\n")
        if data != "Successfully verified":
            pressedKey = True
            Is_End = True
            break


if __name__ == "__main__":
    while True:
        username = input("username: ")
        print("")
        password = input("password: ")
        print("")
        
        url = "http://87.251.88.14:80/login"

        payload = {
            'username': username,
            'password': password,
            'client_id': '123',
            'productName' : "blackjack"
            }

        response = requests.request("POST", url, data=payload)
        data = response.json()["data"]
        
        print(data)
        print("")
        
        if data == "Successfully verified":
            break
        
    Thread(target=pressKey).start()
    Thread(target=userVerify, args=(url, payload, )).start()
    Strategy()
