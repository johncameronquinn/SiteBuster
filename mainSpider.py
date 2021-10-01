#!/usr/bin/env python2.7
import os
import sys

##
# Tutorial on how to use BeautifulSoup
# https://www.dataquest.io/blog/web-scraping-tutorial-python/
##
from bs4 import BeautifulSoup

##
# Urllib used to open websites
#tutorial and documentation found at link below
# https://docs.python.org/2/library/urllib2.html
##
import requests
import urllib3

##
#tutorial on how to use regular expressions
# https://docs.python.org/2/howto/regex.html
##
import re

##
# Python threading library with information about
#threads, semaphores, and locks
# https://docs.python.org/2/library/threading.html
##
import threading
from threading import Lock


import signal

##
# tutorial on QUEUES
# https://docs.python.org/2/library/queue.html#module-Queue
##
import queue

##
# heap documentation for python 2+
# https://docs.python.org/2/library/heapq.html
##
import heapq #by default this is a minheap, we will need to flip it

##
# tutorial / documentation on dictionaries in python 2
# https://docs.python.org/2/library/collections.html#collections.defaultdict
##
from collections import defaultdict

#CONFIG VARIABLES
MAX_CONNECTIONS = 300
MAX_THREADS = 12
MAX_RETRIES = 1
DEFAULT_URL = "https://compsci.cofc.edu"
DEFAULT_DEPTH = 2

#GLOBAL VARIABLES
ACTIVE_THREADS = []
ACTIVE_THREADS_WORK = {} #Dict of threadID to work to be done
WORK_QUEUE = []
CURRENT_QUEUE_SIZE = 0
QUEUE_MUTEX = Lock()

NUM = 0
SEARCH = "None"

LINKS_LIST = defaultdict(list)
#RESULTS = []
RESULTS = defaultdict(list)

#CONSTANTS
QUIT = -1
GO = 0
UNSET = -1
SUCCESS = 0
FAILED = -1


## STOPLIGHT GOES ERWEREEEEREREREHH
msignal = QUIT  ##brakes on by default
##


##
# tutorial on classes in python
# https://www.w3schools.com/python/python_classes.asp
##

# In order to sort our urls by something, we're creating this object
# the heapq function will run the __lt__ function to do its sorting therefor it's compatible
class PendingURL:
    url = "unset"
    currentdepth = UNSET
    maxdepth = UNSET

    def __init__(self, url, currentdepth, maxdepth):
        self.url = url
        self.currentdepth = currentdepth
        self.maxdepth = maxdepth

    def __lt__(self, other):
        return self.currentdepth > other ## flipped to turn the minheap into a maxheap

EMPTY_URL = PendingURL("unset",UNSET,UNSET) ##used elsewhere

def signal_handler(incomingsignal, frame):
    print('Signal caught, shutting down' + str(signal) + str(frame))
    global mSignal
    mSignal = QUIT
    sys.exit(0)

############################
#
# THREAD POOL CLASSES
#
### I was trying to put these in an object, but I can't figure out the scoping
### so that they can still access the parseURL method. Guess they stay here?

## Fire up the threads
def startAllThreads():
    global mSignal
    mSignal = GO
    count = 0
    while count is not MAX_THREADS:
        ACTIVE_THREADS.append(threading.Thread(target = workingThreadLooper, args = ()))
        ACTIVE_THREADS[-1].start()
        count += 1

def stopAllThreads():
    global mSignal
    mSignal = QUIT
    for thread in ACTIVE_THREADS:
        thread.join()

# look for keys in the work dict, if values are empty, give them URLS 
def runThreadPool():
    try:
        while(mSignal is not QUIT): ##check queue, assign 
            global CURRENT_QUEUE_SIZE
            print(CURRENT_QUEUE_SIZE)
            QUEUE_MUTEX.acquire()
            stillworking = False

            for threadID in ACTIVE_THREADS_WORK: # walk through all running threads
                if threadID is not None: # active thread
                    if ACTIVE_THREADS_WORK.get(threadID) is not EMPTY_URL: ## this one still is working
                        stillworking = True
                    elif CURRENT_QUEUE_SIZE is not 0: ## give it work
                        ACTIVE_THREADS_WORK[threadID] = heapq.heappop(WORK_QUEUE)
                        CURRENT_QUEUE_SIZE = CURRENT_QUEUE_SIZE - 1
                        stillworking = True
                    
            if stillworking:
                QUEUE_MUTEX.release()
            else: 
                print("Work queue is now empty, exiting...")
                QUEUE_MUTEX.release()
                return
              
    except:
        print("command received, shutting down...")
        stopAllThreads()

        
def workingThreadLooper():
    global mSignal
    #register myself with work queue
    ACTIVE_THREADS_WORK[threading.current_thread()]=EMPTY_URL
    
    ##run while it has work, until told not to
    while(mSignal is not QUIT):
        #QUEUE_MUTEX.acquire()
        myURL = ACTIVE_THREADS_WORK.get(threading.current_thread())
        #QUEUE_MUTEX.release()
        if myURL is not EMPTY_URL:
            outcome = FAILED
            attempt = 0
            ## repeat attempts until something clicks
            while (outcome is not SUCCESS and attempt is not MAX_RETRIES):
                outcome = parseURL(myURL)
                attempt +=1
                parseURL(myURL)
           #QUEUE_MUTEX.acquire()
            ACTIVE_THREADS_WORK[threading.current_thread()]=EMPTY_URL
           # QUEUE_MUTEX.release()


#
# I've changed this to be using dummy values to make testing and whatnot far easier,
# It's just a bunch of hardcoded stuff, and it's just trying to get follow every link to the
# full depth every time. Our full functionanlity of having it only return links where
# the field is found can be cleanly built on top of this
#

def initialize():
    global NUM
    global SEARCH
    #signal.signal(signal.SIGINT, signal_handler)
    #signal.signal(signal.SIGTERM, signal_handler)

    ##
    # site used to learn how to get user input
    # https://www.pythonforbeginners.com/basics/getting-user-input-from-the-keyboard
    ##
    
    site = input("Enter the target base URL [ " + DEFAULT_URL + " ]") or DEFAULT_URL
    depth = DEFAULT_DEPTH 
    #input("Enter the depth of links to be followed [ " + str(DEFAULT_DEPTH) + " ]") or DEFAULT_DEPTH

    type(site)
    type(depth)

    #return site, depth, MAX_CONNECTIONS

    print("1: Email Address")
    print("2: Phone Number")
    print("3: All emails")
    num = input("Which would you like to find? ") 
    num = int(num)
    print(type(num))
    if num == 1:
        search = input("Enter the email address you'd like to search for: ")
        type(search)
        #print search
        NUM = num
        SEARCH = search
        return site, depth, MAX_CONNECTIONS, num, search
    elif num == 2:
        #has to be in the same format, ex. 843.805.5507
        search = input("Enter the phone number you'd like to seach for: ")
        type(search)
        #print search
        NUM = num
        SEARCH = search
        return site, depth, MAX_CONNECTIONS, num, search
    elif num == 3:
        print("Searching all emails")
        search = "email"
        NUM = num
        SEARCH = search
        return site, depth, MAX_CONNECTIONS, num, search
    else:
        print("Not a valid number ... exiting")
        sys.exit(0)

#
# big complicated regex function taken from django that just makes sure it's a valid url
# I emailed Munsell about whether or not it's okay for us to use it, we can find another way to
# validate the URL's if needed. This one just werks(TM)
#
# returns: true or false
#

def validateURL(url):
    if url is None:
        return False

    ## source https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not ##
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://n
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex,url) is not None


# root recursive method, gets the ball rolling
def performSearch(url, maxdepth):
    print("starting search on site: " + url)

    baseurl = PendingURL(url,0,maxdepth)
    QUEUE_MUTEX.acquire();
    global CURRENT_QUEUE_SIZE
    CURRENT_QUEUE_SIZE = CURRENT_QUEUE_SIZE + 1
    heapq.heappush(WORK_QUEUE,baseurl)
    QUEUE_MUTEX.release();

    return

def emailSearchRE(html):
    #print(html)
    emails = []
    if (NUM == 3):
        ##
        # different tutorial on regex
        # with an example for matching emails
        # using regex from site
        # https://developers.google.com/edu/python/regular-expressions
        ##
        emails = re.findall(r'[\w\.-]+@[\w\.-]+',html)
        return emails
    elif (NUM == 2 or NUM==1):
        if SEARCH in html:
            emails.append(SEARCH)
            return emails

#
# The big "does stuffs" method, which parses a given url link, recursively calling itself on any
# subordinate urls found. The multithreading magic happens in the way this method recursively functions:
# each URL it finds and deems to be valid will spawn a thread to follow that url, calling another instance
# of this same function. At the end of the method, the thread will wait ala thread.join() on each of its
# child threads.
#
# In this manner, the spider threads tend to explode outwards, with each parent waiting on it's respective
# children. This is opposed to the main thread managing all children
#


def parseURL(toParse):

    # this is where it will wait first for permission from the semaphore for a connection    
    connectionLimitingSemaphore.acquire()

    # has a high frequency of failure, this is what we retry
    try:
        page = urllib2.urlopen(toParse.url).read()
    except Exception:
        connectionLimitingSemaphore.release()
        return FAILED

    soup = BeautifulSoup(page,'html.parser')
    soup.prettify()

    connectionLimitingSemaphore.release()

    # grabs all links
    linksObject = soup.find_all('a', href= True)

    urlResults = []
    body = soup.get_text()
    addToResults = emailSearchRE(body) ## parses HTML for emails regex
    if addToResults is not None:
        for i in range(len(addToResults)):
            RESULTS[threading.current_thread()].append(toParse.url)
            RESULTS[threading.current_thread()].append(addToResults[i])

    # QUEUES UP NEW URLS TO BE SEARCHED
    #
    # In this new version, the act of "doing" the work is separated from where it gets done
    # This loop finds every link that is to be explored, and adds it to the queue as needed
    #
    for link in linksObject:
        #print(link.get('href'))
        if(validateURL(toParse.url)):
            LINKS_LIST[threading.currentThread()].append(link.get('href'))
            #newIDscnt = newIDscnt + 1
            if (toParse.currentdepth+1 != toParse.maxdepth):
                newURL = PendingURL(link.get('href'),toParse.currentdepth+1,toParse.maxdepth)

                QUEUE_MUTEX.acquire();
                global CURRENT_QUEUE_SIZE
                CURRENT_QUEUE_SIZE += 1
                heapq.heappush(WORK_QUEUE,newURL)
                print("added " + link.get('href') + " to work queue for parsing")
                QUEUE_MUTEX.release();     
        else:
            print("invalid url " + link + " detected, ignoring...")

    return SUCCESS


def writeLinks(linksList, outfile):
    file =open(outfile, "w")
    for threadID in linksList:
        print("Writing links for thread ID + " + str(threadID))
        #file.write("At Depth: " + str(threadID) + "\n")
        for entry in linksList[threadID]:
            file.write(str(entry) + "\n")
    #file.write(linksList)
    print("Writing to outfile: " + outfile)
    #print("...not yet implemented.")
    file.close()

def queueSizeUpdate():
    print("Size of current queue: " + str(CURRENT_QUEUE_SIZE))

#############################################################################3
#
#  WHERE THE MAGIC HAPPENS
#
############

#gets user input and stores in vaiables
#add num and search
site, depth, maxconnections, num, search= initialize()
print("Website to search: " + site)
print("Depth of search: " + str(depth))
print("Max simulataneous connections: " + str(maxconnections))
print ("")

connectionLimitingSemaphore = threading.BoundedSemaphore(maxconnections)
searchingSemaphore = threading.BoundedSemaphore(1)

performSearch(site, depth)

startAllThreads()
runThreadPool()
stopAllThreads()


print("Final returned list.")

if(len(RESULTS) ==0):
    if(NUM==1):
        print("The email address " + SEARCH + " was not found")
    elif(NUM==2):
        print("The phone number " + SEARCH + " was not found")
    elif(NUM==3):
        print("There were no emails found at depth")
else:
    print("Outputting results to file result.txt")
    writeLinks(RESULTS, "results.txt")
    #print(RESULTS)
# write the link object to the output file

writeLinks(LINKS_LIST, "outfile.txt")
