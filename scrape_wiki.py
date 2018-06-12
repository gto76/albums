#!/usr/local/bin/python3
#
# Usage: .py 
# 

import json
import os
import re
import sys
import urllib.request
from http.cookiejar import CookieJar


BASE = 'https://en.wikipedia.org/wiki/'
MSG = 'Wikipedia does not have an article with this exact name'


def main():
    albums = read_json_file('albumdata.json')
    for album in albums['albums']:
        scrape_album(album['name'])


def scrape_album(name):
    print(name)
    band, album = name.split(' - ', maxsplit=1)
    options = [f'{album}_({band}_album)', f'{album}_(album)', album]
    for option in options:
        print(option)
        html = get_html(BASE + option)
        if html:
            print(option)
            break


def get_html(url):
    try:
        html = scrape(url)
        html = str(html.read())
    except urllib.error.HTTPError:
        return None
    

###
##  UTIL
#

def read_json_file(filename):
    with open(filename, encoding='utf-8') as file:
        return json.load(file)


def scrape(url):
    cj = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    try:
        return opener.open(url)
    except ValueError:
        error("Invalid URL: " + url)


def error(msg):
  msg = os.path.basename(__file__)+": "+msg
  print(msg, file=sys.stderr)
  sys.exit(1)


if __name__ == '__main__':
    main()
