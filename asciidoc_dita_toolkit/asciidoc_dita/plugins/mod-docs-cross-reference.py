#!/usr/bin/python

import os
import re
import sys
import argparse
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

parser = argparse.ArgumentParser(description="A script to update AsciiDoc xrefs.")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-r', '--recursive', action='store_true', help='Run recursively from the current directory.')
group.add_argument('-b', '--book', help='Complete path to your master.adoc file.')


# Match IDs at the top of the file
id_in_regex = re.compile(r'''(?<=['"])[^_"']+''')

# Match include lines. This is for recursively traversing a book from master.adoc
include_in_regex = re.compile(r'(?<=^include::)[^[]+')

# Match xrefs. The negative look-ahead (?!.*\.adoc#) prevents modifying already-modifed xref links.
link_in_regex = re.compile(r'(?<=xref:)(?!.*\.adoc#)([^\[]+)(\[.*?\])')

# The id_map dictionary maps the ID as the key and the file as the value
id_map = {}

# I need to keep track of files
bread_crumbs = []


## Walk all files from master.adoc down
## Read ID and create map

def file_id_map(file, bread_crumbs):
    if file in bread_crumbs:
        return

    bread_crumbs.append(file)
    path = os.path.dirname(file)

    with open(file, 'r', encoding='utf-8') as f:
        print(f"Reading file {file}.")
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
                    file_id_map(file_path, bread_crumbs)
                else:
                    continue
        except Exception as e:
            print(Highlighter(f"Error reading {file}: {e}").warn())
            return


def link_updater(regex_match):

    link_id = regex_match.group(1).split('_')[0]
    file_name = os.path.basename(id_map.get(link_id, ''))
    if not file_name:
         print(Highlighter(f"Warning: ID '{link_id}' not found in id_map.").warn())
         return regex_match.group(0)
    print(Highlighter(f"Fix found! moving {regex_match.group(0)} to {file_name}#{regex_match.group(1)}{regex_match.group(2)}").bold())
    return(f"{file_name}#{regex_match.group(1)}{regex_match.group(2)}")


## Walk all files from master.adoc down
## Use look up map to replace link

def editor():
    for file in set(id_map.values()):
        contents = []
        updates = []
        with open(file, 'r', encoding='utf-8') as f:
            print(f"Checking file {file}.")
            try:
                lines = f.readlines()
                for line in lines:
                    contents.append(line)
            except Exception as e:
                print(Highlighter(f"Error reading {file}: {e}").warn())
                sys.exit()
        
        for line in contents:
             updated_line = link_in_regex.sub(link_updater, line)
             updates.append(updated_line)
        with open(file, 'w', encoding='utf-8') as f:
            f.writelines(updates)

def tree_walker(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file == "master.adoc":
                full_path = os.path.join(root, file)
                file_id_map(full_path, [])


if __name__ == '__main__':
    args = parser.parse_args()
    
    if args.recursive:
        tree_walker(".")
    elif args.book:
        master_file = args.book
        file_id_map(master_file, [])

    editor()
    print(Highlighter("Complete!").bold())
