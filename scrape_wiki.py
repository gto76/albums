#!/usr/local/bin/python3
#
# Usage: .py 
# 

import re
import sys
import urllib.request
from http.cookiejar import CookieJar


BASE = 'https://en.wikipedia.org/wiki/'
MSG = 'Wikipedia does not have an article with this exact name'


def main():
    # Smash_(The_Offspring_album)
    album_name = 'https://en.wikipedia.org/wiki/Smash_(The_Offspring_album)'
    try:
        html = scrape(album_name)
        html = str(html.read())
    except urllib.error.HTTPError:
        print('No page')
    

###
##  UTIL
#

def read_file(filename):
    with open(filename, encoding='utf-8') as file:
        return file.readlines()


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