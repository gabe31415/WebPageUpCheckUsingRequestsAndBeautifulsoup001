import os
import requests
from bs4 import BeautifulSoup

web01Url01 = os.getenv('web01Url01')
web01Username01 = os.getenv('web01Username01')
web01Password01 = os.getenv('web01Password01')
web01Content01 = os.getenv('web01Content01')

if web01Url01 == None:
    print("web01Url01 NOT configured")
    exit()
if web01Username01 == None:
    print("web01Username01 NOT configured")
    exit()
if web01Password01 == None:
    print("web01Password01 NOT configured")
    exit()
if web01Content01 == None:
    print("web01Content01 NOT configured")
    exit()

loginData = {
    '__LASTFOCUS' : None,
    '__EVENTTARGET' : None,
    '__EVENTARGUMENT' : None,
    '__EVENTVALIDATION': None,
    '__VIEWSTATE': None,
    'fakeusernameremembered': None,
    'fakepasswordremembered': None,
    'TextBoxUserName': web01Username01,
    'TextBoxPassword': web01Password01,
    'ButtonLogin' : 'Login'
}

def checkFail():
    # increment fail counter
    # if fail counter max, run "escalation"
    
    # place holder
    print("checkFailed")

def checkSuccess():
    # if fail counter not 0, reset to 0, send alert that check is now succeeding

    # place holder
    print("checkSucceeded")
    

def pageCheck():
    with requests.Session() as s:
        r = s.get(web01Url01)
        soup = BeautifulSoup(r.content, 'html.parser')
        loginData['__EVENTVALIDATION'] = soup.find('input', attrs={'name': '__EVENTVALIDATION'})['value']
        loginData['__VIEWSTATE'] = soup.find('input', attrs={'name': '__VIEWSTATE'})['value']
        r = s.post(web01Url01, data = loginData)
        soup = BeautifulSoup(r.content, 'html.parser')
        anchors = soup.find_all('a')
        validated = False
        for a in anchors:
            if a.text == web01Content01:
                validated = True
        if validated:
            checkSuccess()
        else:
            checkFail()

def recheckLogic():
    # how long to wait between checks, perhaps dependent on current fail count?
    pass

pageCheck()

recheckLogic()
