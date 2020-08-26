#!/usr/bin/env python3

import re
import requests
import argparse
import os


occurrences = {}


def tex_check(texfile):
    re_url = re.compile('\\\\url\{.*?\}')
    re_href = re.compile('\\\\href\{.*?\}\{')
    lcount = 0
    with open(texfile, 'r') as infile:
        for line in infile.readlines():
            lcount += 1
            for found in re_url.findall(line):
                add_occurrence(found[5:-1], texfile, lcount)
            for found in re_href.findall(line):
                add_occurrence(found[6:-2], texfile, lcount)


def add_occurrence(url, texfile, line):
    global occurrences
    if url not in occurrences.keys():
        url, status_code = check_url(url)
        occurrences[url] = {'status_code': status_code, 'occurrences': []}
    occurrences[url]['occurrences'].append('%s:%04d' % (texfile, line))


def recursive_check(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.tex'):
                fullpath = os.path.join(root, file)
                print("# Reading:", fullpath)
                tex_check(fullpath)


def check_url(url):
    url = url.replace('\\%', '%')
    print("## Checking:", url)
    r = requests.get(url)
    return url, r.status_code


def print_occurrences():
    global occurrences
    print()
    for url in sorted(occurrences.keys()):
        status_code = occurrences[url]['status_code']
        print("%d --- %s" % (status_code, url))
        for o in sorted(occurrences[url]['occurrences']):
            print("- %s" % o)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tex_file_or_dir", help="The file or directory to analyze.")
    args = parser.parse_args()
    if os.path.isdir(args.tex_file_or_dir):
        recursive_check(args.tex_file_or_dir)
        print_occurrences()
    elif os.path.isfile(args.tex_file_or_dir):
        tex_check(args.tex_file_or_dir)
        print_occurrences()
    else:
        print('No such file or directory:', args.tex_file_or_dir)
