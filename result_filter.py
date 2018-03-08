#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import codecs
import sys


def operation(inf, outf, target_lids, before, after):
    done = set()
    for line in inf:
        items = line[:-1].split("\t")

        orig_lids = set([int(lid) for lid in items[4][1:-1].split("|")])
        out_lids = set([int(lid) for lid in items[8][1:-1].split("|")])

        orig_ginata = items[2] + '.' + items[6]
        if orig_ginata in done:
            continue

        if len(orig_lids & target_lids) >= 1 and\
                len(out_lids & target_lids) == 0:
            if not before:
                continue
            pass
        elif len(orig_lids & target_lids) == 0 and \
                len(out_lids & target_lids) >= 1:
            if not after:
                continue
        else:
            continue

        cost_orig = int(items[2])
        cost_ginata = int(items[6])
        outf.write("%d\t" % abs(cost_orig - cost_ginata))
        outf.write(line)
        done.add(orig_ginata)


def get_opts():
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--bunrui", "-b", required=True)
    oparser.add_argument("--input", "-i", default="-", required=False)
    oparser.add_argument("--output", "-o", default="-", required=False)
    oparser.add_argument("--before", default=False, action="store_true")
    oparser.add_argument("--after", default=False, action="store_true")
    oparser.add_argument("--key", default='体-生産物-食料')
    return oparser.parse_args()


def main():
    opts = get_opts()

    lids = set()
    with codecs.open(opts.bunrui, "r", "utf8") as f:
        for line in f:
            if opts.key in line:
                lid = line[:-1].split('\t')[1]
                lids.add(int(lid))
    if len(lids) == 0:
        sys.stderr.write("No targets\n")
        sys.exit(1)

    if opts.input == "-":
        inf = iter(sys.stdin.readline, "")
    else:
        inf = codecs.open(opts.input, "r", "utf8")

    if opts.output == "-":
        outf = sys.stdout
    else:
        outf = codecs.open(opts.output, "w", "utf8")

    if not(opts.before and opts.after):
        pass
    elif opts.before and opts.after:
        sys.stderr.write("--before and --after and exclusive\n")
        sys.exit(1)
    operation(inf, outf, lids, opts.before, opts.after)


if __name__ == '__main__':
    main()
