#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygtrie
import argparse
import codecs
import sys
import os
import shutil
import subprocess


def get_trie_from_freqdata(freq_path):
    sys.stderr.write('Get freq...\n')
    tr = pygtrie.CharTrie()
    with codecs.open(freq_path, 'r', 'utf-8') as inf:
        for idx, line in enumerate(inf):
            if idx % 1000 == 0:
                sys.stderr.write('\r%d' % idx)
            items = line[:-1].split('\t')
            if len(items) != 2:
                continue
            word = items[0]
            freq = int(items[1])
            tr[word] = freq
    sys.stderr.write('\n done!\n')
    return tr


def _make_matrix(in_path, out_path, target=0):
    sys.stderr.write('Make matrix...\n')
    with codecs.open(in_path, 'r', 'utf-8') as inf, \
            codecs.open(out_path, 'w', 'utf-8') as outf:
        for lid, line in enumerate(inf):
            if lid == 0:
                outf.write(line)
                continue
            elif lid % 1000 == 0:
                sys.stderr.write('\r%d' % lid)

            items = line.split(' ')
            if len(items) != 3:
                raise SyntaxError
            lid, rid, cost = [int(val) for val in items]

            # BOS/EOS(id=0) との連接コストを一律0にする
            if lid == 0 or rid == 0:
                cost = 0
            outf.write('%d %d %d\n' % (lid, rid, cost))
    sys.stderr.write('\n done!\n')


def _make_lex(freqs, lex_in_path, lex_out_path):
    sys.stderr.write('Make lex.csv...\n')
    with codecs.open(lex_in_path, 'r', 'utf-8') as inf, \
            codecs.open(lex_out_path, 'w', 'utf-8') as outf:
        for idx, line in enumerate(inf):
            surf = line[:line.find(',')]
            freq = freqs.get(surf)
            if freq is None:  # 低頻度語を削る
                continue

            fields = line.split(',')
            if len(fields) >= 5 and fields[4] in ['記号', '補助記号', '感動詞']:
                continue

            outf.write(line[:-1])  # without \n
            outf.write(",%d\n" % freq)  # 頻度情報を素性に足す


def operation(freq_path, unidic_path, out_path, command):
    out_src_path = os.path.join(out_path, 'src')
    out_bin_path = os.path.join(out_path, 'bin')
    os.makedirs(out_src_path, exist_ok=True)
    os.makedirs(out_bin_path, exist_ok=True)

    sys.stderr.write('Copy...\n')
    shutil.copy(os.path.join(unidic_path, 'dicrc'), out_src_path)
    shutil.copy(os.path.join(unidic_path, 'dicrc'), out_bin_path)
    fnames = ['char.def', 'feature.def', 'left-id.def',
              'model.def', 'rewrite.def', 'right-id.def', 'unk.def']
    for fname in fnames:
        shutil.copy(os.path.join(unidic_path, fname), out_src_path)

    lex_in_path = os.path.join(unidic_path, 'lex.csv')
    lex_out_path = os.path.join(out_src_path, 'lex.limited.csv')
    freqs = get_trie_from_freqdata(freq_path)
    _make_lex(freqs, lex_in_path, lex_out_path)

    _make_matrix(os.path.join(unidic_path, 'matrix.def'),
                 os.path.join(out_src_path, 'matrix.def'))

    mycmd = '%s -f utf8 -t utf8 -d %s -o %s' %\
            (command, out_src_path, out_bin_path)
    sys.stderr.write('Exec\n %s\n' % mycmd)
    subprocess.check_output(mycmd, shell=True)
    sys.stderr.write('\n done!\n')


def get_opts():
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--unidic", "-u", required=True)
    oparser.add_argument("--freq", required=True)
    oparser.add_argument("--output", "-o", required=True)
    oparser.add_argument("--command",
                         default=os.path.expanduser(
                             '~/local/libexec/mecab/mecab-dict-index'))
    return oparser.parse_args()


def main():
    opts = get_opts()
    operation(opts.freq, opts.unidic, opts.output, opts.command)


if __name__ == '__main__':
    main()
