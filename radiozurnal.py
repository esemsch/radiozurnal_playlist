import requests
import codecs
import re
from datetime import datetime,timedelta
import os.path

URL_PATTERN = "http://www.rozhlas.cz/radiozurnal/playlisty?den="
REGEX = re.compile(r'<li><span class="time">\s*(\S.*?\S)\s*</span> <span class="interpret">\s*(\S.*?\S)\s*</span> - <span class="track">\s*(\S.*?\S)\s*</span></li>',re.S)
OUTPUT_DIR="playlists"

def getDayFileName(day,tmp=False):
    return OUTPUT_DIR+("_tmp" if tmp else "")+"/"+day+".csv"

def downloadDay(day):
    url = URL_PATTERN + day
    print("Getting: "+day)

    httpResponse = requests.get(url)
    body = httpResponse.text

    matches = REGEX.findall(body)

    outputFile = codecs.open(getDayFileName(day,True),"w",'utf-8')

    for m in matches:
        for x in [m[1],";",m[2],";",m[0],"\n"]:
            outputFile.write(x)

    outputFile.close()

def readDay(day,its,tmp=False):
    inputFile = codecs.open(getDayFileName(day,tmp),"r",'utf-8')

    recs = [r.split(";") for r in inputFile]

    for r in recs:
        if its.get(r[0]) == None:
            its[r[0]] = []

        if not r[1] in its[r[0]]:
            its[r[0]].append(r[1])

def getReadDays():
    readDays = []
    for d in os.listdir(OUTPUT_DIR):
        readDays.append(d[:-4])
    return readDays

def getUnreadDays():
    unreadDays = []
    for i in range(1,8):
        day = (datetime.today()-timedelta(days=i)).strftime('%d.%m.%Y')
        if not os.path.isfile(getDayFileName(day)):
            unreadDays.append(day)
    return unreadDays

unreadDays = getUnreadDays()
readDays = getReadDays()

print("Read: "+str(sorted(readDays)))
print("Unread: "+str(sorted(unreadDays)))

existingIts = {}
for d in readDays:
    readDay(d,existingIts)

newIts = {}
for d in unreadDays:
    downloadDay(d)
    readDay(d,newIts,True)

def printResults(its):
    sortd = sorted(its.items(), key = lambda x: x[0])

    for rec in sortd:
        print(rec[0])
        for s in rec[1]:
            print("\t"+s)

def diffResults(existing, new):
    diff = {}
    for k,v in new.items():
        ev = existing.get(k)
        if ev is None:
            diff[k]=v
        else:
            for ns in v:
                if not ns in ev:
                    if diff.get(k) is None:
                        diff[k]=[]
                    diff[k].append(ns)
    return diff

printResults(existingIts)
print(">>>>>>>>>>>>>>>>>>> NEW <<<<<<<<<<<<<<<<<")
printResults(diffResults(existingIts,newIts))
