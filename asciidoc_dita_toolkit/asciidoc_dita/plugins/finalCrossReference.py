#!/usr/bin/python

import os
import re
import sys

# Use the Highligher class modify text in a consistent way
# For example:
# print(Highlighter("text").warn()
# Change the definitions in the class to modify the text
# output uniformly everywhere.

class Highlighter(object):
    def __init__(self, text):
       self.text = text
    def warn(self):
        return('\033[0;31m' + self.text + '\033[0m')
    def bold(self):
        return('\033[1m' + self.text + '\033[0m')
    def highlight(self):
        return('\033[0;36m' + self.text + '\033[0m')


# Match IDs at the top of the file
id_in_regex = re.compile(r='(?<=['"])[^_"']+')

# Match include lines. This is for recursively traversing a book from master.adoc
include_in_regex = re.compile(r='(?<=^include::)[^[]+')

# Match xrefs. The negative look-ahead (?!.*\.adoc#) prevents modifying already-modifed xref links.
link_in_regex = re.compile(r'(?<=xref:)(?!.*\.adoc#)([^_\[]+)(\[.*?\])')


id_map = {}

## Walk all files from master.adoc down
## Read ID and create map

def file_id_map(file):
    # built from scratch on each iteration. Does this even work?
    include_list = []

    path = os.path.dirname(file)

    with open(file, 'r', encoding='utf-8') as f:
        try:
            lines = f.readlines()
            for line in lines:
                match_id = id_in_regex.search(line.strip())
                match_include = include_in_regex.search(line.strip())

                # If there there's an ID, we add it to the dictionary
                if match_id:
                    id = match_id.group()
                    id_map[id] = file

                # Keep track of all file paths as well
                elif match_include:
                    include_path = match_include.group()
                    combined_path = os.path.join(path, include_path)
                    file_path = os.path.normpath(combined_path)

                    print(f'Adding {file_path}')
                    include_list.append(file_path)

                else:
                    continue
        except Exception as e:
            print(Highlighter(f"Error reading {file}: {e}").warn())
            sys.exit()
    for i in include_list:
        # I'm worried that the include list is going to be wiped out with the recursion ⚠️
        file_id_map(i)

## Walk all files from master.adoc down
## Use look up map to replace link

def editor():
    for i in id_map:
        file = os.path.dirname(id_map[i]):
        with open(file, 'r+', encoding='utf-8'):
            try:
                links = f.readlines()
                for line in lines:
                    match = link_in_regex.search(line.strip())                
                    if match:
                    # stuck
                    # re.sub(?)
            except:
                print(Highlighter(f"Error reading {file}: {e}").warn())
                sys.exit()
 
