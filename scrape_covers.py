#!/usr/local/bin/python3
#
# Usage: scrape_covers.py 
# 

import re
import sys
import json
import subprocess


def main():
    songs = read_json_file('albumdata.json')
    for song in songs['albums']:
        name = song['name']
        link = song['image']
        image_name = f'img/covers/{name}.jpg'
        command = ['wget', link, '-O', image_name]
        print(command)
        subprocess.run(command, stdout=subprocess.PIPE) 
    

###
##  UTIL
#

def read_json_file(filename):
    with open(filename, encoding='utf-8') as file:
        return json.load(file)


if __name__ == '__main__':
    main()