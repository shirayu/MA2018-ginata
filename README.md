
# なぎた読みの自動作成の試み

[![Apache License](http://img.shields.io/badge/license-APACHE2-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0)

- [NLP2018(言語処理学会第24回年次大会)](http://www.anlp.jp/nlp2018/)の[ワークショップ 形態素解析の今とこれから](https://sites.google.com/view/nlp2018ws)で発表
    - 林部祐太「ぎなた読みの自動生成の試み」，言語処理学会第24回年次大会ワークショップ 形態素解析の今とこれから．(2018.3.16) [[slide]](https://hayashibe.jp/publications/MA2018.pdf)
- ウェブコーパスにおいて一定の出現頻度以上のあるn-gramに対し，異なる形態素分割が可能か調査する
    - [出力例](https://github.com/shirayu/MA2018-ginata/releases)



## Requirements

1. 自分でn-gramコーパスを用意するか，[NINJAL Web Japanese Corpus](http://nwjc-data.ninjal.ac.jp)から以下のファイルをダウンロード・展開する
    - ``NWJC-surface-1gram.zip``
    - ``NWJC-surface-2gram.zip`` (または任意のn-gram)
    - このn-gram作成に使われた辞書と，ぎなた読み探索に用いる辞書が一致するとは限らないことに留意
2. [UniDic](http://unidic.ninjal.ac.jp)のウェブサイトから現代書き言葉UniDicをダウンロード・展開する
3. [wlsp2unidic](http://pj.ninjal.ac.jp/corpus_center/goihyo.html)をダウンロード・展開する
4. [MeCab](http://taku910.github.io/mecab/)をインストールし，ライブラリを利用できるようにする


## Usage

```bash
# 頻度が300回以上の1gram, 2gramを抽出
#  形態素単位はUniDicとは限らないことに注意
zcat data/NWJC-surface-1gram/*gz | nkf -w | python3 ./ngram_filter.py -n 1 --th 300 > data/1gram.300.txt
zcat data/NWJC-surface-2gram/*gz | nkf -w | python3 ./ngram_filter.py -n 2 --th 300 > data/2gram.300.txt

# オリジナルのUnidicを加工したMeCab辞書を作成
#  1-gramが一定数以上ある形態素のみ使う
#  記号などは除外
#  BOS/EOSとの連接コストは0になる
python3 ./convert_unidic.py --unidic /path/to/unidic --freq data/1gram.300.txt -o data/mydic

# C++プログラムをコンパイル
g++ -lmecab ./discover-ginata.cpp -o discover-ginata

# 異分割の探索
cat ./data/2gram.300.txt | ./discover-ginata -d ./data/mydic/bin | gzip > data/result.2gram.gz

# 分類語彙表を使って結果をフィルタリングする
#   コスト差を示す先頭カラムが追加される
#   ここでは異分割に食料を意味する形態素を含む場合のみを出力している
zcat data/result.2gram.gz | python3 ./result_filter.py -b ./data/wlsp2unidic/BunruiNo_LemmaID.txt --key 体-生産物-食料-食料 --after
```


## Related Work

- [金久保正明，形態素解析手法と通俗的単語群に基づく類音文変換システム，情報処理学会論文誌，Vol.54, No.7, pp.1937-1950, 2013)](https://ci.nii.ac.jp/naid/110009586575/)
- [Hajime Morita, Daisuke Kawahara and Sadao Kurohashi: Morphological Analysis for Unsegmented Languages using Recurrent Neural Network Language Model, Proceedings of EMNLP 2015, pp.2292-2297, 2015](http://aclweb.org/anthology/D/D15/D15-1276.pdf)
- [林部祐太, 日本語部分形態素アノテーションコーパスの構築, 情報処理学会第231回自然言語処理研究会, NL-231-9, pp.1-8, 2017](https://hayashibe.jp/publications/NL231.pdf)
    - [Fairy Morphological Annotated Corpus](https://github.com/FairyDevicesRD/FairyMaCorpus)


## LICENSE

- [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0)


