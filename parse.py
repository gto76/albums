#!/usr/local/bin/python3
#
# Usage: parse.py 
# 
# To install Image library run:
#   pip3 install pillow

import json
from itertools import count
import math
import re
import sys

from PIL import Image
import matplotlib.pyplot as plt


MAP_IMAGE = "worldmap.jpg"
HTML_TOP = "html-top.html"
HTML_TEXT = "html-text.html"
HTML_BOTTOM = "html-bottom.html"

DRAW_YEARLY_DISTRIBUTION_PLOT = True
DRAW_HEATMAP = True

HEAT_FACTOR = 0.5
HEAT_DISTANCE_THRESHOLD = 5
HEATMAP_ALPHA = 180
ALPHA_CUTOFF = 0.15


###
##  MAIN
#

def main():
    readme = getFileContents("list-of-albums")
    albumData = readJson("albumData.json")
    listOfAlbums = getListOfAlbums(readme)
    noOfAlbums = len(listOfAlbums)

    generate_release_dates_chart(albumData)
    generate_heat_map(albumData)

    out_md = generate_md_file(readme, albumData, listOfAlbums, noOfAlbums)
    out_html = generate_html_file(albumData, listOfAlbums, noOfAlbums)

    writeToFile('README.md', out_md)
    writeToFile('index.html', out_html)


def generate_md_file(readme, albumData, listOfAlbums, noOfAlbums):
    out = str(noOfAlbums) + " " + getText(readme)
    out += generateList(listOfAlbums, albumData)
    out += '<hr>\n'

    if DRAW_YEARLY_DISTRIBUTION_PLOT:
        out += "\nRelease Date — Year\n------\n![yearly graph](year-distribution.png)"

    if DRAW_HEATMAP:
        out += "\nStudio Location\n------\n![heatmap](heatmap.png)"

    return out


def generate_html_file(albumData, listOfAlbums, noOfAlbums):
    out = ''.join(getFileContents(HTML_TOP))
    out += str(noOfAlbums) + " " + '\n'.join(getFileContents(HTML_TEXT))
    out += generate_html_list(listOfAlbums, albumData)
    out += '<br><br><br><br><hr>'

    if DRAW_YEARLY_DISTRIBUTION_PLOT:
        out += '<h2><a href="#release-dates" name="release-dates">#</a>Release Date — Year</h2>\n'
        out += '<img src="year-distribution.png" alt="Release dates" width="920"/>\n'

    if DRAW_HEATMAP:
        out += '<h2><a href="#studio-locations" name="studio-locations">#</a>Studio Location</h2>\n'
        out += '<img src="heatmap.png" alt="Studio Locations" width="920"/>\n'

    return out + ''.join(getFileContents(HTML_BOTTOM))


def getListOfAlbums(readme):
    listOfAlbums = []
    for line in readme:
        if line.startswith('####'):
            listOfAlbums.append(line.strip("####").replace('*', '').strip())
    return list(reversed(listOfAlbums))


def getText(readme):
    out = ""
    for line in readme:
        if not line.startswith('####'):
            out += line
    return out


def generateList(listOfAlbums, albumData):
    out = ""
    counter = count(1) #len(listOfAlbums)
    for albumName in listOfAlbums:
        artist, album = albumName.split(' - ', maxsplit=1)
        formatedName = f'"{album}" — {artist}'
        # formatedName = albumName.replace(" - ", ", '", 1) + "'"
        out += "### " + str(next(counter)) + " | " + formatedName + "  \n"
        slogan = getSlogan(albumName, albumData)
        if slogan:
            out += '_“'+slogan+'”_  \n' 
            out += '  \n'
        cover = getCover(albumName, albumData)
        if cover:
            out += cover
    return out


def generate_html_list(listOfAlbums, albumData):
    out = ""
    counter = count(1) #len(listOfAlbums)
    for albumName in listOfAlbums:
        artist, album = albumName.split(' - ', maxsplit=1)
        formatedName = f'"{album}" — {artist}'
        # formatedName = albumName.replace(" - ", ", '", 1) + "'"
        album_name_abr = albumName.replace(' ', '')
        start = '<h2><a href="#'+album_name_abr+'" name="' \
                + album_name_abr+'">#</a>'
        out += start + str(next(counter)) + " | " + formatedName + "</h2>\n"
        slogan = getSlogan(albumName, albumData)
        if slogan:
            out += '<i>' + slogan + '</i><br><br>\n'
        cover = getCover(albumName, albumData)
        if cover:
            out += cover
    return out


def getSlogan(albumName, albumData):
    for album in albumData['albums']:
        if albumName == album['name'] and album['slogan']:
            return album['slogan']
    return None


def getCover(albumName, albumData):
    image_name = albumName.replace('?', '').replace('!', '')
    imageLink = f'img/covers/{image_name}.jpg' #getImageLink(albumName, albumData)
    if imageLink is None:
        return
    out = getYouTubeLink(albumName)
    out += '<img src="' + imageLink
    out += '" alt="cover" height="306"/></a>\n'
    return out


def getYouTubeLink(albumName):
    out = '<a target="_blank" href="https://www.youtube.com/results?search_query=' \
          + albumName.replace('-', '').replace(' ', '+') + '+full+album"> '
    if 'Dicky B. Hardy' in albumName:
        out = '<a target="_blank" href="https://youtu.be/8iwk7_O97Pw?list=PLaeyhQtn9sJxmrSPAMmmLd4H35jAmFcF1">'
    if 'Matter' in albumName:
        out = '<a target="_blank" href="https://www.youtube.com/results?search_query=' \
          + albumName.replace('-', '').replace(' ', '+') + '"> ' 
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
    out += "\nRelease Dates\n------\n![yearly graph](year-distribution.png)"
    return out


def generate_release_dates_chart(albumData):
    listOfYears = getYears(albumData)
    albumsPerYear = getAlbumsPerYear(listOfYears)
    yearRange = getYearRange(listOfYears)

    set_plt_size(plt, width=22, height=8, font_size=18)

    # fig_size = plt.rcParams["figure.figsize"]
    # Set figure width to 12 and height to 9
    # fig_size[0] = 20
    # fig_size[1] = 6
    # plt.rcParams["figure.figsize"] = fig_size

    x_ticks = [listOfYears[0]-1] + yearRange + [listOfYears[-1]+1]
    x_ticks = [a for a in x_ticks if a % 2 == 0]
    plt.xticks(x_ticks, [get_year_xlabel(a) for a in x_ticks])

    y = albumsPerYear
    x = yearRange
    plt.bar(x, y, color="blue")

    plt.savefig('year-distribution.png', transparent=True)


def set_plt_size(plt, width, height, font_size):
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = width
    fig_size[1] = height
    plt.rcParams["figure.figsize"] = fig_size
    plt.rcParams.update({'font.size': font_size})


def get_year_xlabel(value):
    value = str(value)[-2:]
    return f"'{value}"


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
## HEAT
#

def generate_heat_map(albumData):
    worldMap = Image.open(MAP_IMAGE)
    worldMap = worldMap.convert("RGBA")
    width = worldMap.size[0]
    height = worldMap.size[1]

    heatMatrix = generateHeatMap(albumData, width, height)
    heatImage = generateHeatImage(heatMatrix)

    worldMap.paste(heatImage, (0, 0), heatImage)
    worldMap.save('heatmap.png')


def generateHeatImage(heatMatrix):
    width = len(heatMatrix[0])
    height = len(heatMatrix)
    image = Image.new('RGBA', (width, height))
    # image = Image.open(MAP_IMAGE)
    pixels = image.load()

    for i in range(image.size[0]):
        for j in range(image.size[1]):
            # brightness = int(heatMatrix[j][i] * 255) / 2
            brightness = heatMatrix[j][i]
            if brightness > 0:
                # rgb = getHeatMapColor2(0, 1, brightness)
                rgb = getHeatMapColor(brightness)
                # r = min(pixels[i, j][0] + rgb[0], 255)
                # g = min(pixels[i, j][1] + rgb[1], 255)
                # b = min(pixels[i, j][2] + rgb[2], 255)
                r = rgb[0]
                g = rgb[1]
                b = rgb[2]
                a = getAlpha(brightness)
                pixels[i, j] = (int(r), int(g), int(b), int(a))

    return image


def getAlpha(brightness):
    if brightness > ALPHA_CUTOFF:
        return HEATMAP_ALPHA
    return brightness / ALPHA_CUTOFF * HEATMAP_ALPHA


def getHeatMapColor2(minimum, maximum, value):
    minimum, maximum = float(minimum), float(maximum)
    ratio = 2 * (value-minimum) / (maximum - minimum)
    b = int(max(0, 255*(1 - ratio)))
    r = int(max(0, 255*(ratio - 1)))
    g = 255 - b - r
    return r, g, b


def getHeatMapColor(value):
    NUM_COLORS = 4
    color = [ [0.0,0.0,1.0], [0.0,1.0,0.0], [1.0,1.0,0.0], [1.0,0.0,0.0] ]

    fractBetween = 0

    if value <= 0:
        idx1 = idx2 = 0
    elif value >= 1:
        idx1 = idx2 = NUM_COLORS-1
    else:
        value = value * (NUM_COLORS-1)
        idx1  = math.floor(value)
        idx2  = idx1+1
        fractBetween = float(value - float(idx1))

    red   = (color[idx2][0] - color[idx1][0])*fractBetween + color[idx1][0]
    green = (color[idx2][1] - color[idx1][1])*fractBetween + color[idx1][1]
    blue  = (color[idx2][2] - color[idx1][2])*fractBetween + color[idx1][2]
    return (red*255, green*255, blue*255)


def generateHeatMap(albumData, width, height):
    out = []
    for y in range(0, height):
        row = []
        for x in range(0, width):
            xx = transposeX(x, width)
            yy = transposeY(y-2, height)
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
    return (HEAT_DISTANCE_THRESHOLD - distance) / HEAT_DISTANCE_THRESHOLD * \
            HEAT_FACTOR


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
