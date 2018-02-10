#!/usr/bin/env python3
# coding: utf-8

import sys
import os
import re

PAT_NLIST  = re.compile(r'^(\d+\. )')   # numbered list
PAT_BLIST1 = re.compile(r'^[\-\*] ')    # bulleted list, the first level
PAT_BLIST2 = re.compile( '^◦\t')        # bulleted list, the second level
PAT_BLIST3 = re.compile( '^▪\t')        # bulleted list, the third level
PAT_LIST_M = re.compile(r'^\s+[\d\*]')  # modified numbered/bulleted list
PAT_BLANK  = re.compile(r'^\s*$')       # blank line

def exporter2bear(src_filepath, out_filepath):

    # title is the file name without file extension
    title = os.path.basename(src_filepath)
    title = os.path.splitext(title)[0]

    # extract tag from dir hierarchy without first level
    tag = os.path.dirname(src_filepath)
    tag = tag.split(os.path.sep)[1:]
    tag = os.path.sep.join(tag).lower()

    # contents of output file
    # the first line is the title, followed by an empty line
    lines = ['# {}'.format(title), '']

    with open(src_filepath, "r", encoding='utf-8') as fin:

        for line in fin:

            # chomp
            line = line.rstrip()

            # if this line is '**', set the previous line as a heading
            if line == "**":
                if len(lines) > 0 and len(lines[-1]) > 0 and lines[-1][0] != '#':
                    lines[-1] = "## {}".format(lines[-1])
            else:
                # we want to indent all list items (better looking in Bear)
                line = re.sub(PAT_NLIST,  "\t\\1", line)
                line = re.sub(PAT_BLIST1, "\t* ", line)
                line = re.sub(PAT_BLIST2, "\t\t* ", line)
                line = re.sub(PAT_BLIST3, "\t\t\t* ", line)

                # remove blank lines between two adjacent list items
                if (re.match(PAT_LIST_M, line)):
                    if (len(lines) > 0 and re.match(PAT_BLANK, lines[-1])):
                        lines.pop()

                # remove tailing *
                line = line.rstrip('*')

                lines.append(line)

        # append tag
        lines.append('')
        lines.append('#{}'.format(tag))

    # write output file
    with open(out_filepath, "w+", encoding='utf-8') as fout:
        fout.write(os.linesep.join(lines))

    print("{}\t: {} #{}".format(src_filepath, title, tag))


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("ERROR: need two arguments: source directory and output directory")
        sys.exit(-1)
    src_dir = sys.argv[1]
    out_dir = sys.argv[2]
    if not os.path.isdir(src_dir):
        print("ERROR: the first argument should be a directory")
        sys.exit(-1)

    # traverse all files in src_dir
    for dirpath, dirnames, filenames in os.walk(src_dir):
        for filename in filenames:

            # bypass non-txt files
            if not filename.endswith('.txt'):
                continue

            src_filepath = os.path.join(dirpath, filename)
            out_filepath = src_filepath.replace(src_dir, out_dir, 1)

            # create output directory if not exist
            os.makedirs(os.path.dirname(out_filepath), exist_ok=True)

            exporter2bear(src_filepath, out_filepath)
