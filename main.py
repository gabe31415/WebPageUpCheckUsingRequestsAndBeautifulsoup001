import datetime
import os
import time

from bs4 import BeautifulSoup
from exchangelib import Account, Credentials, Mailbox, Message
import requests

failCount = 0
maxFailCount = 3
nextCheck = 60 # seconds until next check when failCount < maxFailCount
maxFailCountReachedNextCheck = 1800 # seconds until next check when maxFailCount reached

# pull confidential variables from environment variables
web01Url01 = os.getenv('web01Url01')
web01Username01 = os.getenv('web01Username01')
web01Password01 = os.getenv('web01Password01')
web01Content01 = os.getenv('web01Content01')
workEmailAddress = os.getenv('workEmailAddress')
workEmailPassword = os.getenv('workEmailPassword')
webPageCheckEmailSubjectLineCustomer02 = os.getenv('webPageCheckEmailSubjectLineCustomer02')
webPageCheckApp01Customer02 = os.getenv('webPageCheckApp01Customer02')

if web01Url01 == None:
    print('web01Url01 NOT configured')
    exit()
if web01Username01 == None:
    print('web01Username01 NOT configured')
    exit()
if web01Password01 == None:
    print('web01Password01 NOT configured')
    exit()
if web01Content01 == None:
    print('web01Content01 NOT configured')
    exit()
if workEmailAddress == None:
    print('workEmailAddress NOT configured')
    exit()
if workEmailPassword == None:
    print('workEmailPassword NOT configured')
    exit()
if webPageCheckEmailSubjectLineCustomer02 == None:
    print('webPageCheckEmailSubjectLineCustomer02 NOT configured')
    exit()
if webPageCheckApp01Customer02 == None:
    print('webPageCheckApp01Customer02 NOT configured')
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
    print('checkFailed')
    print('Incrementing fail count')
    global failCount
    failCount += 1
    print('failCount is now', str(failCount))
    if failCount < maxFailCount:
        time.sleep(nextCheck)
    else:
        print('Sending failure email!')
        sendEmail()
        print('Fail threshold reached sleeping for', str(maxFailCountReachedNextCheck), 'seconds!')
        time.sleep(maxFailCountReachedNextCheck)
    pageCheck()



def checkSuccess():
    print('checkSucceeded', datetime.datetime.now())
    failCount = 0
    print('sleeping for', str(nextCheck), 'seconds.')
    time.sleep(nextCheck)
    pageCheck()

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

def emailConnection():
    credentials = Credentials(workEmailAddress, workEmailPassword)
    a = Account(workEmailAddress, credentials=credentials, autodiscover=True)
    return a

def sendEmail():
    a = emailConnection()
    m = Message(
        account=a,
        folder=a.sent,
        subject=webPageCheckEmailSubjectLineCustomer02,
        body=webPageCheckApp01Customer02+' is DOWN!',
        to_recipients=[workEmailAddress]
    )
    m.send_and_save()

pageCheck()
