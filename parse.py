#!/usr/bin/python
#
# Usage: parse.py 
# 

import json
import re
import sys

def main():
    readme = getFileContents("list-of-albums")
    albumdata = readJson("albumdata.json")
    listOfAlbums = getListOfAlbums(readme)

    noOfAlbums = len(listOfAlbums)
    out = str(noOfAlbums) + " " + getText(readme)
    out += generateList(listOfAlbums, albumdata)
    print(out)


def getListOfAlbums(readme):
    listOfAlbums = []
    for line in readme:
        if line.startswith('####'):
            listOfAlbums.append(line.strip("####").strip())
    return listOfAlbums


def getText(readme):
    out = ""
    for line in readme:
        if not line.startswith('####'):
            out += line
    return out


def generateList(listOfAlbums, albumdata):
    out = ""
    counter = len(listOfAlbums)
    for album in listOfAlbums:
        out += "#### " + str(counter) + " | " + album + "\n"
        counter -= 1
    return out


# UTIL:

def getFileContents(fileName):
    with open(fileName) as f:
        return f.readlines()


def readJson(fileName):
    with open(fileName) as f:    
        return json.load(f)

if __name__ == '__main__':
  main()
