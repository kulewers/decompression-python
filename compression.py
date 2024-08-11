#!/usr/bin/env python3

import argparse
import sys
import csv
from collections import defaultdict
import heapq

termCode = "<compr!␚"


class HuffLeafNode:
    def __init__(self, element, weight):
        self._element = element
        self._weight = weight

    def value(self):
        return self._element

    def weight(self):
        return self._weight

    @staticmethod
    def isLeaf():
        return True


class HuffInternalNode:
    def __init__(self, left, right, weight):
        self._left = left
        self._right = right
        self._weight = weight

    def left(self):
        return self._left

    def right(self):
        return self._right

    def weight(self):
        return self._weight

    @staticmethod
    def isLeaf():
        return False


class HuffTree:
    def __init__(self, weight, element=None, left=None, right=None):
        if element and not left and not right:
            self._root = HuffLeafNode(element, weight)
        elif left and right and not element:
            self._root = HuffInternalNode(left, right, weight)

    def root(self):
        return self._root

    def weight(self):
        return self._root.weight()

    def __eq__(self, other):
        return True if self._root.weight() == other.weight() else False

    def __lt__(self, other):
        return True if self._root.weight() < other.weight() else False

    def __gt__(self, other):
        return True if self._root.weight() > other.weight() else False


def createFreqList(source):
    freq = defaultdict(lambda: 0)
    while True:
        c = source.read(1)
        if not c:
            break
        freq[c] += 1
    return freq.items()


def buildTree(frequencies):
    treeHeap = list(map(lambda x: HuffTree(
        element=x[0], weight=x[1]), frequencies))
    heapq.heapify(treeHeap)
    while len(treeHeap) > 1:
        tmp1 = heapq.heappop(treeHeap)
        tmp2 = heapq.heappop(treeHeap)
        tmp3 = HuffTree(left=tmp1.root(), right=tmp2.root(),
                        weight=tmp1.weight() + tmp2.weight())

        heapq.heappush(treeHeap, tmp3)
    return tmp3


def createPrefixCodeTable(tree):
    table = {}
    walkTree(tree.root(), table)
    return table


def walkTree(node, table, code=''):
    if node.isLeaf():
        table[node.value()] = code
        return

    walkTree(node.left(), table, code + '0')
    walkTree(node.right(), table, code + '1')
    return


def writeToOut(table, outFilename, inFilename):
    with open(outFilename, 'w') as output:
        tablelist = [(k, v) for k, v in table.items()]
        writer = csv.writer(output)
        for row in tablelist:
            writer.writerow(row)
        output.write(termCode)
        with open(inFilename, 'r') as input:
            writeBin = ''
            while True:
                while len(writeBin) >= 8:
                    utf8Rerp = chr(int(writeBin[0:8], 2))
                    output.write(utf8Rerp)
                    writeBin = writeBin[8:]
                char = input.read(1)
                if not char:
                    break
                code = table[char]
                writeBin = writeBin + code
            if len(writeBin):
                lastByte = writeBin.ljust(8, '0')
                utf8Rerp = chr(int(lastByte, 2))
                output.write(lastByte)


def main():
    parser = argparse.ArgumentParser(
        prog='compression',
        description='compress files',
    )
    parser.add_argument('filename')
    parser.add_argument('-o', '--output', required=True)
    args = parser.parse_args()
    filename = args.filename
    try:
        with open(filename) as f:
            frequencies = createFreqList(f)
        tree = buildTree(frequencies)
        prefixCodeTable = createPrefixCodeTable(tree)
        writeToOut(prefixCodeTable, args.output, filename)
    except IOError:
        print("Could not open file: ", filename)
        sys.exit(60)


if __name__ == "__main__":
    main()
