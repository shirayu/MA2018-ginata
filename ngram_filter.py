#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import codecs
import sys


def operation(inf, outf, n, th):
    for line in inf:
        items = line[:-1].split("\t")
        if len(items) != 2:
            continue
        freq = int(items[1])
        if freq < th:
            continue
        words = items[0].split(" ")
        if len(words) != n:
            continue
        outf.write(line)


def get_opts():
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", default="-", required=False)
    oparser.add_argument("--output", "-o", default="-", required=False)
    oparser.add_argument("--ngram", "-n", default=2, required=False, type=int)
    oparser.add_argument("--threshold", "--th",
                         default=300, required=False, type=int)
    return oparser.parse_args()


def main():
    opts = get_opts()
    if opts.input == "-":
        inf = iter(sys.stdin.readline, "")
    else:
        inf = codecs.open(opts.input, "r", "utf8")

    if opts.output == "-":
        outf = sys.stdout
    else:
        outf = codecs.open(opts.output, "w", "utf8")
    operation(inf, outf, opts.ngram, opts.threshold)


if __name__ == '__main__':
    main()
