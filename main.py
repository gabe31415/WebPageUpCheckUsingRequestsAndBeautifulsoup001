import datetime
import os
import time

from bs4 import BeautifulSoup
from exchangelib import Account, Credentials, Mailbox, Message
import requests

MAXFAILCOUNT = 3
NEXTCHECK = 60 
MAXFAILCOUNTREACHEDNEXTCHECK = 1800 

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

def checkFail(failCount):
    print('checkFailed')
    print('Incrementing fail count')
    failCount += 1
    print('failCount is now', str(failCount))
    if failCount < MAXFAILCOUNT:
        time.sleep(NEXTCHECK)
    return failCount


def maxFail(failCount):
    print('Sending failure email!')
    try:
        sendEmail()
    except:
        "failed to send email. I'm ignoring this for now. "
    print('Fail threshold reached sleeping for', str(MAXFAILCOUNTREACHEDNEXTCHECK), 'seconds!')
    # if you're just going to sleep, and try again...
    # you should really send an email when it's back up
    time.sleep(MAXFAILCOUNTREACHEDNEXTCHECK)
    failCount = 0
    return failCount


def checkSuccess():
    print('checkSucceeded', datetime.datetime.now())
    failCount = 0
    print('sleeping for', str(NEXTCHECK), 'seconds.')
    time.sleep(NEXTCHECK)
    return failCount

def pageCheck(failCount):
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
            failCount = checkSuccess()
            return failCount
        failCount = checkFail(failCount)
        return failCount


def main(failCount, deathcount):
    # fC starts at 0
    while failCount < MAXFAILCOUNT:
        try:
            failCount = pageCheck(failCount)
        except Exception as e:
            print("Something unknown has occurred.")
            print(e)
            exit()
    failCount = maxFail(failCount)
    deathcount += 1
    while deathcount < 100:
        # 100 death knells, meaning, what, 300 + failures?
        main(failCount, deathcount)
    exit()


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

if __name__ == "__main__":
    main(0, 0)