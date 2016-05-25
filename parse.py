#!/usr/bin/python
#
# Usage: parse.py 
# 

import json
import re
import sys
import matplotlib.pyplot as plt

def main():
    readme = getFileContents("list-of-albums")
    albumData = readJson("albumData.json")
    listOfAlbums = getListOfAlbums(readme)

    noOfAlbums = len(listOfAlbums)
    out = str(noOfAlbums) + " " + getText(readme)
    out += generateList(listOfAlbums, albumData)

    listOfYears = getYears(albumData)
    albumsPerYear = getAlbumsPerYear(listOfYears)
    yearRange = getYearRange(listOfYears)
    # print([[1,1],[2,1],[3,2]])
    # plt.plot([1,1],[2,1])
    # plt.ylabel('some numbers')
    # plt.show()

    y = albumsPerYear
    x = yearRange
    width = 1/1.5
    plt.bar(x, y, width, color="blue")
    plt.savefig('year-distribution.png')

    out += "Yearly distribution\n------\n![yearly graph](year-distribution.png)"

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
        formatedName = albumName.replace(" - ", ", '", 1) + "'"
        out += "#### " + str(counter) + " | " + formatedName + "\n"
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
    out += '" alt="cover" height="306"/></a>\n'
    return out


def getImageLink(albumName, albumData):
    for album in albumData['albums']:
        if albumName == album['name'] and album['image']:
            return album['image']
    return None


# GRAPH:

def getYears(albumData):
    listOfYears = []
    for album in albumData['albums']:
        if album['year']:
            listOfYears.append(album['year'])
    listOfYears.sort()
    return listOfYears


def getAlbumsPerYear(listOfYears):
    out = []
    for year in range(listOfYears[0], listOfYears[-1]+1):
        out.append(listOfYears.count(year))
    return out
    

def getYearRange(listOfYears):
    return list(range(listOfYears[0], listOfYears[-1]+1))


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
