#!/usr/bin/python3
#
# Usage: parse.py 
# 
# To install Image library run:
#   pip3 install pillow

import json
import math
import re
import sys

from PIL import Image
import matplotlib.pyplot as plt
#from mpl_toolkits.basemap import Basemap


MAP_IMAGE = "worldmap.jpg"

DRAW_YEARLY_DISTRIBUTION_PLOT = True
DRAW_HEATMAP = True
HEAT_DISTANCE_THRESHOLD = 5


###
##  MAIN
#

def main():
    # setup Lambert Conformal basemap.
    # set resolution=None to skip processing of boundary datasets.
    # m = Basemap(width=12000000,height=9000000,projection='lcc',
    #             resolution=None,lat_1=45.,lat_2=55,lat_0=50,lon_0=-107.)
    # m.shadedrelief()
    # plt.show()

    readme = getFileContents("list-of-albums")
    albumData = readJson("albumData.json")
    listOfAlbums = getListOfAlbums(readme)

    noOfAlbums = len(listOfAlbums)
    out = str(noOfAlbums) + " " + getText(readme)
    out += generateList(listOfAlbums, albumData)

    if DRAW_YEARLY_DISTRIBUTION_PLOT:
        out = addYearlyDistributionPlot(out, albumData)

    if DRAW_HEATMAP:
        out = addHeatMap(out, albumData)

    # writeToFile('README.md', out)


###
## HEAT
#

def addHeatMap(out, albumData):
    worldMap = Image.open(MAP_IMAGE)
    width = worldMap.size[0]
    height = worldMap.size[1]
    heatMatrix = generateHeatMap(albumData, width, height)
    image = generateHeatImage(heatMatrix)
    image.show()


def generateHeatImage(heatMatrix):
    width = len(heatMatrix[0])
    height = len(heatMatrix)
    # image = Image.new('RGB', (width, height), "black")
    image = Image.open(MAP_IMAGE)
    pixels = image.load()

    for i in range(image.size[0]):
        for j in range(image.size[1]):
            brightness = int(heatMatrix[j][i] * 255) / 2
            if brightness > 0:
                r = min(pixels[i, j][0] + brightness, 255)
                g = min(pixels[i, j][1] + brightness, 255)
                b = min(pixels[i, j][2] + brightness, 255)
                pixels[i, j] = (int(r), int(g), int(b))

    return image


def generateHeatMap(albumData, width, height):
    out = []
    for y in range(0, height):
        row = []
        for x in range(0, width):
            xx = transposeX(x, width)
            yy = transposeY(y, height)
            heat = getHeat(xx, yy, albumData)
            row.append(heat)
        out.append(row)
    return out


def transposeX(x, width):
    if x == 0:
        return -180
    else:
        return (((x / width) - 0.5) * 2) * 180


def transposeY(y, height):
    if y == 0:
        return 90
    else:
        return -(((y / height) - 0.5) * 2) * 90


def getHeat(x, y, albumData):
    heat = 0
    for album in albumData['albums']:
        if 'long' not in album or 'lat' not in album:
            continue
        distance = math.hypot(x - album["long"], y - album["lat"])
        heat += distanceToHeat(distance)
        if heat > 1:
            heat = 1
    return heat


def distanceToHeat(distance):
    if distance > HEAT_DISTANCE_THRESHOLD:
        return 0
    return (HEAT_DISTANCE_THRESHOLD - distance) / HEAT_DISTANCE_THRESHOLD


###
##
#

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


###
##  PLOT
#

def addYearlyDistributionPlot(out, albumData):
    listOfYears = getYears(albumData)
    albumsPerYear = getAlbumsPerYear(listOfYears)
    yearRange = getYearRange(listOfYears)

    fig_size = plt.rcParams["figure.figsize"]
    # Set figure width to 12 and height to 9
    fig_size[0] = 20
    fig_size[1] = 6
    plt.rcParams["figure.figsize"] = fig_size

    y = albumsPerYear
    x = yearRange
    plt.bar(x, y, color="blue")

    plt.savefig('year-distribution.png')

    out += "Yearly distribution\n------\n![yearly graph](year-distribution.png)"
    return out


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


###
##  UTIL
#

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
