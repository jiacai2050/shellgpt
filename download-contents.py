#!/usr/bin/env python
# coding: utf-8

import json
import csv
import subprocess

# https://github.com/f/awesome-chatgpt-prompts/
url = 'https://raw.githubusercontent.com/f/awesome-chatgpt-prompts/main/prompts.csv'


def main():
    out = subprocess.getoutput(f'curl -s {url}')
    rdr = csv.reader(out.split('\n'))
    contents = {}
    for row in rdr:
        name = (
            row[0]
            .replace('(', '')
            .replace(')', '')
            .replace(' ', '-')
            .replace('`', '')
            .replace('/', '-')
            .lower()
        )
        if name == 'act':
            # skip first row
            continue

        content = row[1]
        contents[name] = content

    with open('contents.json', 'w') as f:
        f.write(json.dumps(contents, indent=4))


if __name__ == '__main__':
    main()
