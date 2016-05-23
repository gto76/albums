#!/usr/bin/python
#
# Usage: parse.py 
# 

import json
import re
import sys

def main():
    readme = getFileContents("list-of-albums")
    albumData = readJson("albumData.json")
    listOfAlbums = getListOfAlbums(readme)

    noOfAlbums = len(listOfAlbums)
    out = str(noOfAlbums) + " " + getText(readme)
    out += generateList(listOfAlbums, albumData)
    writeToFile('README.md', out)


def getListOfAlbums(readme):
    listOfAlbums = []
    for line in readme:
        if line.startswith('####'):
            listOfAlbums.append(line.strip("####").replace('*', '').strip())
    return listOfAlbums


def getText(readme):
    out = ""
    for line in readme:
        if not line.startswith('####'):
            out += line
    return out


def generateList(listOfAlbums, albumData):
    out = ""
    counter = len(listOfAlbums)
    for albumName in listOfAlbums:
        out += "#### " + str(counter) + " | " + albumName + "\n"
        cover = getCover(albumName, albumData)
        if cover:
            out += cover
        counter -= 1
    return out


def getCover(albumName, albumData):
    imageLink = getImageLink(albumName, albumData)
    if imageLink is None:
        return
    out = '<a href="https://www.youtube.com/results?search_query='
    out += albumName.replace('-', '').replace(' ', '+') + 'full+album"> '
    out += '<img src="' + imageLink
    out += '" alt="cover" width="206"/></a>\n'
    return out


def getImageLink(albumName, albumData):
    for album in albumData['albums']:
        if albumName == album['name'] and album['image']:
            return album['image']
    return None


# UTIL:

def getFileContents(fileName):
    with open(fileName) as f:
        return f.readlines()


def readJson(fileName):
    with open(fileName) as f:    
        return json.load(f)


def writeToFile(fileName, contents):
    f = open(fileName,'w')
    f.write(contents) 
    f.close()

if __name__ == '__main__':
  main()
