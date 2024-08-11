#!/usr/bin/env python3

import argparse
import sys
import csv
from io import StringIO

termCode = "<compr!␚"


def main():
    parser = argparse.ArgumentParser(
        prog='decompression',
        description='decompresses files',
    )
    parser.add_argument('filename')
    parser.add_argument('-o', '--output', required=True)
    args = parser.parse_args()
    filename = args.filename
    try:
        with open(filename, 'r') as input:
            csvTable = ""
            while True:
                c = input.read(1)
                if not c:
                    break
                csvTable = csvTable + c
                if termCode in csvTable:
                    csvTable = csvTable[:-(len(termCode)+1)]
                    break

            reader = csv.reader(StringIO(csvTable))
            decode = {}
            for row in reader:
                decode[row[1]] = row[0]

            with open(args.output, 'w') as output:
                bits = ''
                while True:
                    c = input.read(1)
                    if not c:
                        break
                    bits = bits + format(ord(c), 'b').rjust(8, '0')
                    while len(bits) > 0:
                        for i in range(1, len(bits)+1):
                            substr = bits[:i]
                            if substr in decode:
                                output.write(decode[substr])
                                bits = bits[i:]
                                break
                        break
    except IOError as e:
      print("Could not open file: ", filename, e)
      sys.exit(60)


if __name__ == '__main__':
    main()
